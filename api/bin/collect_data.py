import os
import sys
import time
import argparse # For --limit argument
from mwrogue.esports_client import EsportsClient
from sqlalchemy import func
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from ..models_base import get_session
from ..scoreboard_game_model import ScoreboardGame
from ..picks_and_bans_model import PicksAndBansS7Model


BATCH_SIZE = 100

# --- Mappings from DB schema column names to API field names ---
DB_TO_API_KEY_MAP_SG = {
    'DateTime_UTC': 'DateTime UTC',
    'Gamelength_Number': 'Gamelength Number',
    'N_Page': 'N Page',
    'N_MatchInTab': 'N MatchInTab',
    'N_MatchInPage': 'N MatchInPage',
    'N_GameInMatch': 'N GameInMatch',
}

DB_TO_API_KEY_MAP_PB = {
    'N_Page': 'N Page',
    'N_TabInPage': 'N TabInPage',
    'N_MatchInPage': 'N MatchInPage',
    'N_GameInPage': 'N GameInPage',
    'N_GameInMatch': 'N GameInMatch',
    'N_MatchInTab': 'N MatchInTab',
    'N_GameInTab': 'N GameInTab',
    'GameID_Wiki': 'GameID Wiki',
}

# --- Database Utility Functions (SQLAlchemy) ---
def get_last_collected_timestamp():
    session = get_session()
    try:
        max_timestamp = session.query(func.max(ScoreboardGame.DateTime_UTC)).scalar()
        if max_timestamp:
            print(f"Successfully fetched last collected timestamp: {max_timestamp}")
            return max_timestamp
        else:
            count = session.query(func.count(ScoreboardGame.GameId)).scalar()
            if count > 0:
                print(f"No valid MAX(DateTime_UTC) found in ScoreboardGames, but table has {count} rows. Treating as fresh start for timestamp.")
            else:
                print("ScoreboardGames table is empty or contains no valid timestamps. Starting fresh.")
            return None
    except Exception as e:
        print(f"SQLAlchemy error in get_last_collected_timestamp: {e}")
        return None
    finally:
        session.close()

# --- Data Insertion Functions (SQLAlchemy) ---
def insert_scoreboard_games_batch(session, data_dicts):
    if not data_dicts: return 0
    objects_to_insert = []
    for api_row_dict in data_dicts:
        model_data = {}
        for model_attr in ScoreboardGame.__table__.columns.keys():
            api_key = DB_TO_API_KEY_MAP_SG.get(model_attr, model_attr)
            if api_key in api_row_dict: # Check if API provided this key
                 model_data[model_attr] = api_row_dict.get(api_key)

        if not model_data.get('GameId'):
            # print(f"Skipping ScoreboardGame data due to missing GameId: {api_row_dict.get('GameId', 'N/A')}") # Can be verbose
            continue
        objects_to_insert.append(model_data)

    if not objects_to_insert:
        # print("No valid ScoreboardGame objects to insert after processing.") # Can be verbose
        return 0

    try:
        stmt = sqlite_insert(ScoreboardGame).values(objects_to_insert)
        stmt = stmt.on_conflict_do_nothing(index_elements=[ScoreboardGame.GameId])
        result = session.execute(stmt)
        print(f"Attempted to insert {len(objects_to_insert)} ScoreboardGames. Rows affected: {result.rowcount}")
        return result.rowcount
    except Exception as e: print(f"SQLAlchemy error during SG batch insert: {e}"); return 0

def insert_picks_and_bans_batch(session, data_dicts):
    if not data_dicts: return 0
    objects_to_insert = []
    for api_row_dict in data_dicts:
        model_data = {}
        for model_attr in PicksAndBansS7Model.__table__.columns.keys():
            api_key = DB_TO_API_KEY_MAP_PB.get(model_attr, model_attr)
            if api_key in api_row_dict: # Check if API provided this key
                model_data[model_attr] = api_row_dict.get(api_key)

        if not model_data.get('UniqueLine'):
            # print(f"Skipping PicksAndBansS7 data due to missing UniqueLine: {api_row_dict.get('UniqueLine', 'N/A')}") # Can be verbose
            continue

        for bool_field_name in ['IsComplete', 'IsFilled']:
            api_val = model_data.get(bool_field_name)
            if isinstance(api_val, str):
                if api_val.lower() in ['true', '1', 'yes', 't']: model_data[bool_field_name] = True
                elif api_val.lower() in ['false', '0', 'no', 'f']: model_data[bool_field_name] = False
                else: model_data[bool_field_name] = None
            elif isinstance(api_val, int): model_data[bool_field_name] = bool(api_val)

        objects_to_insert.append(model_data)

    if not objects_to_insert:
        # print("No valid PicksAndBansS7 objects to insert after processing.") # Can be verbose
        return 0

    try:
        stmt = sqlite_insert(PicksAndBansS7Model).values(objects_to_insert)
        stmt = stmt.on_conflict_do_nothing(index_elements=[PicksAndBansS7Model.UniqueLine])
        result = session.execute(stmt)
        print(f"Attempted to insert {len(objects_to_insert)} PicksAndBansS7. Rows affected: {result.rowcount}")
        return result.rowcount
    except Exception as e: print(f"SQLAlchemy error during PB batch insert: {e}"); return 0

# --- Main Data Collection Logic ---
def collect_data(process_limit=0):
    site = EsportsClient('lol')

    all_pb_fields_list = [col.name for col in PicksAndBansS7Model.__table__.columns]
    all_sg_fields_list = [col.name for col in ScoreboardGame.__table__.columns]

    offset = 0
    total_pb_fetched_this_run = 0
    total_sg_fetched_this_run = 0
    sg_references_processed_count = 0

    last_timestamp = get_last_collected_timestamp()
    print(f"Starting collection. Last collected timestamp: {last_timestamp}")

    while True:
        if process_limit > 0 and sg_references_processed_count >= process_limit:
            print(f"Process limit of {process_limit} ScoreboardGames references reached.")
            break

        current_batch_fetch_limit = BATCH_SIZE
        if process_limit > 0:
            remaining_to_fetch = process_limit - sg_references_processed_count
            if remaining_to_fetch < current_batch_fetch_limit:
                current_batch_fetch_limit = remaining_to_fetch

        if current_batch_fetch_limit <= 0 and process_limit > 0:
             print("Limit effectively reached, breaking loop.")
             break

        print(f"\nFetching SG refs, offset: {offset}, batch_limit: {current_batch_fetch_limit}, processed_count: {sg_references_processed_count}/{process_limit if process_limit > 0 else 'unlimited'}")

        sg_query_params = {
            'tables': "ScoreboardGames", 'fields': "GameId, DateTime_UTC",
            'order_by': "DateTime_UTC DESC", 'limit': current_batch_fetch_limit, 'offset': offset
        }
        if last_timestamp: sg_query_params['where'] = f"DateTime_UTC < '{last_timestamp}'"

        print(f"Querying ScoreboardGames refs: {sg_query_params}")
        sg_references = []
        try:
            sg_references = site.cargo_client.query(**sg_query_params)
        except Exception as e:
            print(f"API error fetching SG refs: {e}. Advancing offset.")
            offset += current_batch_fetch_limit
            time.sleep(30)
            continue

        if not sg_references:
            print("No more ScoreboardGames data to fetch.")
            break

        sg_references_processed_count += len(sg_references) # Increment after successful fetch

        current_batch_game_ids = list(set([item['GameId'] for item in sg_references if item.get('GameId')]))
        print(f"Fetched {len(sg_references)} SG refs, {len(current_batch_game_ids)} unique GameIDs.")

        if not current_batch_game_ids:
            print("No GameIDs in current batch, advancing offset.")
            offset += len(sg_references) if sg_references else current_batch_fetch_limit
            if not sg_references or len(sg_references) < current_batch_fetch_limit:
                 print("Assuming end of data due to empty/partial sg_references batch.")
                 break
            time.sleep(10)
            continue

        pb_references_for_game_ids = []
        for idx, chunk in enumerate([current_batch_game_ids[i:i + 20] for i in range(0, len(current_batch_game_ids), 20)]):
            if not chunk: continue
            params = {'tables': "PicksAndBansS7", 'fields': "UniqueLine, GameId", 'where': f"GameId IN ('{ "','".join(chunk) }')"}
            print(f"Querying PB refs (chunk {idx+1}): {params}")
            try:
                refs = site.cargo_client.query(**params)
                if refs: pb_references_for_game_ids.extend(refs)
            except Exception as e: print(f"API error fetching PB refs chunk. Error: {e}. Skipping."); time.sleep(5); continue

        pb_unique_lines = list(set([r['UniqueLine'] for r in pb_references_for_game_ids if r.get('UniqueLine')]))
        game_ids_for_full_fetch = list(set([r['GameId'] for r in pb_references_for_game_ids if r.get('GameId')]))
        print(f"Found {len(pb_references_for_game_ids)} PB refs for {len(game_ids_for_full_fetch)} GameIDs, with {len(pb_unique_lines)} unique UniqueLines.")

        if not game_ids_for_full_fetch and not pb_unique_lines:
            print("No PB data for this SG batch. Advancing main offset.")
            offset += len(sg_references)
            if len(sg_references) < current_batch_fetch_limit: break
            time.sleep(10)
            continue

        session = get_session()
        try:
            if game_ids_for_full_fetch:
                sg_api_data = []
                for idx, chunk in enumerate([game_ids_for_full_fetch[i:i + 50] for i in range(0, len(game_ids_for_full_fetch), 50)]):
                    if not chunk: continue
                    params = {'tables': "ScoreboardGames", 'fields': ", ".join(all_sg_fields_list), 'where': f"GameId IN ('{ "','".join(chunk) }')"}
                    print(f"Querying full SG (chunk {idx+1}): {params}")
                    try: data = site.cargo_client.query(**params); sg_api_data.extend(data if data else [])
                    except Exception as e: print(f"API error full SG. Error: {e}. Skip."); time.sleep(5); continue
                if sg_api_data: print(f"Debug Keys SG (first): {list(sg_api_data[0].keys()) if sg_api_data else 'N/A'}")
                print(f"Fetched {len(sg_api_data)} full SG entries.")
                count = insert_scoreboard_games_batch(session, sg_api_data); total_sg_fetched_this_run += count

            if pb_unique_lines:
                pb_api_data = []
                for idx, chunk in enumerate([pb_unique_lines[i:i + 50] for i in range(0, len(pb_unique_lines), 50)]):
                    if not chunk: continue
                    params = {'tables': "PicksAndBansS7", 'fields': ", ".join(all_pb_fields_list), 'where': f"UniqueLine IN ('{ "','".join(chunk) }')"}
                    print(f"Querying full PB (chunk {idx+1}): {params}")
                    try: data = site.cargo_client.query(**params); pb_api_data.extend(data if data else [])
                    except Exception as e: print(f"API error full PB. Error: {e}. Skip."); time.sleep(5); continue
                if pb_api_data: print(f"Debug Keys PB (first): {list(pb_api_data[0].keys()) if pb_api_data else 'N/A'}")
                print(f"Fetched {len(pb_api_data)} full PB entries.")
                count = insert_picks_and_bans_batch(session, pb_api_data); total_pb_fetched_this_run += count

            session.commit(); print("Committed batch.")
        except Exception as e: print(f"Critical DB/processing error: {e}. Rollback."); session.rollback()
        finally: session.close()

        offset += len(sg_references)
        if len(sg_references) < current_batch_fetch_limit:
            print("Fetched fewer SG refs than batch limit, assuming end of relevant data.")
            break

        print("Waiting 10s before next main batch fetch...")
        time.sleep(10)

    print(f"\nCollection run complete. SG rows affected: {total_sg_fetched_this_run}, PB rows affected: {total_pb_fetched_this_run}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Collect League of Legends match data from Leaguepedia.")
    parser.add_argument(
        "--limit", type=int, default=500,
        help="Max ScoreboardGames references to process. 0 for no limit. Default: 500."
    )
    args = parser.parse_args()
    print(f"Starting data collection (SQLAlchemy) with limit: {args.limit if args.limit > 0 else 'No limit'}")
    collect_data(process_limit=args.limit)
    print("Data collection process finished.")
