import sqlite3
from mwrogue.esports_client import EsportsClient
import time

DB_NAME = 'league_data.db'
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

# --- Database Utility Functions ---
def get_db_connection():
    return sqlite3.connect(DB_NAME)

def get_last_collected_timestamp():
    """Fetches the most recent DateTime_UTC from the local ScoreboardGames table."""
    import os
    if not os.path.exists(DB_NAME):
        print(f"Database file {DB_NAME} does not exist. Starting fresh.")
        return None

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(DateTime_UTC) FROM ScoreboardGames")
        result = cursor.fetchone()
        if result and result[0]:
            print(f"Successfully fetched last collected timestamp: {result[0]}")
            return result[0]
        else:
            # Check if table is empty or all timestamps are NULL
            cursor.execute("SELECT COUNT(*) FROM ScoreboardGames")
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"No valid MAX(DateTime_UTC) found in ScoreboardGames, but table has {count} rows. Treating as fresh start for timestamp.")
            else:
                print("ScoreboardGames table is empty or contains no valid timestamps. Starting fresh.")
            return None
    except sqlite3.Error as e:
        print(f"SQLite error in get_last_collected_timestamp: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_existing_game_ids():
    """Fetches all existing GameIds from the ScoreboardGames table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT GameId FROM ScoreboardGames")
    result = cursor.fetchall()
    conn.close()
    return {row[0] for row in result}

def get_existing_pb_unique_lines():
    """Fetches all existing UniqueLines from the PicksAndBansS7 table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT UniqueLine FROM PicksAndBansS7")
    result = cursor.fetchall()
    conn.close()
    return {row[0] for row in result}

# --- Data Insertion Functions ---
def insert_scoreboard_games_batch(data):
    if not data:
        return 0
    conn = get_db_connection()
    cursor = conn.cursor()

    placeholders = ', '.join(['?'] * len(data[0]))
    # Assuming data[0] contains keys in the correct order matching the table schema
    # This needs to be robust. Let's get column names from the schema.
    cursor.execute("PRAGMA table_info(ScoreboardGames)")
    schema_columns = [col[1] for col in cursor.fetchall()]

    placeholders = ', '.join(['?'] * len(schema_columns))

    ordered_data = []
    for row_dict in data: # data from API
        ordered_row = []
        for db_col_name in schema_columns: # e.g., "DateTime_UTC"
            api_key = DB_TO_API_KEY_MAP_SG.get(db_col_name, db_col_name)
            ordered_row.append(row_dict.get(api_key))
        ordered_data.append(tuple(ordered_row))

    try:
        cursor.executemany(f"INSERT OR IGNORE INTO ScoreboardGames ({', '.join(schema_columns)}) VALUES ({placeholders})", ordered_data)
        conn.commit()
        inserted_rows = cursor.rowcount
        print(f"Inserted {inserted_rows} new rows into ScoreboardGames.")
        return inserted_rows
    except sqlite3.Error as e:
        print(f"SQLite error during ScoreboardGames batch insert: {e}")
        return 0
    finally:
        conn.close()

def insert_picks_and_bans_batch(data):
    if not data:
        return 0
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(PicksAndBansS7)")
    schema_columns = [col[1] for col in cursor.fetchall()]

    placeholders = ', '.join(['?'] * len(schema_columns))

    ordered_data = []
    for row_dict in data: # data from API
        ordered_row = []
        for db_col_name in schema_columns: # e.g., "GameID_Wiki"
            api_key = DB_TO_API_KEY_MAP_PB.get(db_col_name, db_col_name)
            ordered_row.append(row_dict.get(api_key))
        ordered_data.append(tuple(ordered_row))

    try:
        cursor.executemany(f"INSERT OR IGNORE INTO PicksAndBansS7 ({', '.join(schema_columns)}) VALUES ({placeholders})", ordered_data)
        conn.commit()
        inserted_rows = cursor.rowcount
        print(f"Inserted {inserted_rows} new rows into PicksAndBansS7.")
        return inserted_rows
    except sqlite3.Error as e:
        print(f"SQLite error during PicksAndBansS7 batch insert: {e}")
        return 0
    finally:
        conn.close()

# --- Main Data Collection Logic ---
def collect_data():
    site = EsportsClient('lol')
    last_timestamp = get_last_collected_timestamp()
    print(f"Starting collection. Last collected timestamp from DB: {last_timestamp}") # Debug print

    # Fields for ScoreboardGames (ensure these match the table definition)
    sg_fields = "SG.OverviewPage, SG.Tournament, SG.Team1, SG.Team2, SG.WinTeam, SG.LossTeam, SG.DateTime_UTC, SG.DST, SG.Team1Score, SG.Team2Score, SG.Winner, SG.Gamelength, SG.Gamelength_Number, SG.Team1Bans, SG.Team2Bans, SG.Team1Picks, SG.Team2Picks, SG.Team1Players, SG.Team2Players, SG.Team1Dragons, SG.Team2Dragons, SG.Team1Barons, SG.Team2Barons, SG.Team1Towers, SG.Team2Towers, SG.Team1Gold, SG.Team2Gold, SG.Team1Kills, SG.Team2Kills, SG.Team1RiftHeralds, SG.Team2RiftHeralds, SG.Team1VoidGrubs, SG.Team2VoidGrubs, SG.Team1Atakhans, SG.Team2Atakhans, SG.Team1Inhibitors, SG.Team2Inhibitors, SG.Patch, SG.LegacyPatch, SG.PatchSort, SG.MatchHistory, SG.VOD, SG.N_Page, SG.N_MatchInTab, SG.N_MatchInPage, SG.N_GameInMatch, SG.Gamename, SG.UniqueLine AS SG_UniqueLine, SG.GameId, SG.MatchId, SG.RiotPlatformGameId, SG.RiotPlatformId, SG.RiotGameId, SG.RiotHash, SG.RiotVersion"

    # Fields for PicksAndBansS7 (ensure these match the table definition)
    pb_fields = "PB.Team1Role1, PB.Team1Role2, PB.Team1Role3, PB.Team1Role4, PB.Team1Role5, PB.Team2Role1, PB.Team2Role2, PB.Team2Role3, PB.Team2Role4, PB.Team2Role5, PB.Team1Ban1, PB.Team1Ban2, PB.Team1Ban3, PB.Team1Ban4, PB.Team1Ban5, PB.Team1Pick1, PB.Team1Pick2, PB.Team1Pick3, PB.Team1Pick4, PB.Team1Pick5, PB.Team2Ban1, PB.Team2Ban2, PB.Team2Ban3, PB.Team2Ban4, PB.Team2Ban5, PB.Team2Pick1, PB.Team2Pick2, PB.Team2Pick3, PB.Team2Pick4, PB.Team2Pick5, PB.Team1, PB.Team2, PB.Winner, PB.Team1Score, PB.Team2Score, PB.Team1PicksByRoleOrder, PB.Team2PicksByRoleOrder, PB.OverviewPage AS PB_OverviewPage, PB.Phase, PB.UniqueLine AS PB_UniqueLine, PB.IsComplete, PB.IsFilled, PB.Tab, PB.N_Page AS PB_N_Page, PB.N_TabInPage AS PB_N_TabInPage, PB.N_MatchInPage AS PB_N_MatchInPage, PB.N_GameInPage AS PB_N_GameInPage, PB.N_GameInMatch AS PB_N_GameInMatch, PB.N_MatchInTab AS PB_N_MatchInTab, PB.N_GameInTab AS PB_N_GameInTab, PB.GameId AS PB_GameId, PB.MatchId AS PB_MatchId, PB.GameID_Wiki"

    # We need to alias columns that have the same name in both tables
    # For simplicity, I'll query PicksAndBansS7 first, then ScoreboardGames for those GameIds.

    # These lists should contain the field names as defined in Leaguepedia's Cargo table schema (typically using underscores)
    all_pb_fields_list = [
        "Team1Role1", "Team1Role2", "Team1Role3", "Team1Role4", "Team1Role5",
        "Team2Role1", "Team2Role2", "Team2Role3", "Team2Role4", "Team2Role5",
        "Team1Ban1", "Team1Ban2", "Team1Ban3", "Team1Ban4", "Team1Ban5",
        "Team1Pick1", "Team1Pick2", "Team1Pick3", "Team1Pick4", "Team1Pick5",
        "Team2Ban1", "Team2Ban2", "Team2Ban3", "Team2Ban4", "Team2Ban5",
        "Team2Pick1", "Team2Pick2", "Team2Pick3", "Team2Pick4", "Team2Pick5",
        "Team1", "Team2", "Winner", "Team1Score", "Team2Score",
        "Team1PicksByRoleOrder", "Team2PicksByRoleOrder", "OverviewPage", "Phase",
        "UniqueLine", "IsComplete", "IsFilled", "Tab",
        "N_Page", "N_TabInPage", "N_MatchInPage", "N_GameInPage", # Using DB schema names
        "N_GameInMatch", "N_MatchInTab", "N_GameInTab",          # Using DB schema names
        "GameId", "MatchId", "GameID_Wiki"                         # Using DB schema names
    ]
    all_sg_fields_list = [
        "OverviewPage", "Tournament", "Team1", "Team2", "WinTeam", "LossTeam",
        "DateTime_UTC", "DST", "Team1Score", "Team2Score", "Winner", "Gamelength", # Using DB schema names
        "Gamelength_Number", "Team1Bans", "Team2Bans", "Team1Picks", "Team2Picks", # Using DB schema names
        "Team1Players", "Team2Players", "Team1Dragons", "Team2Dragons", "Team1Barons",
        "Team2Barons", "Team1Towers", "Team2Towers", "Team1Gold", "Team2Gold",
        "Team1Kills", "Team2Kills", "Team1RiftHeralds", "Team2RiftHeralds",
        "Team1VoidGrubs", "Team2VoidGrubs", "Team1Atakhans", "Team2Atakhans",
        "Team1Inhibitors", "Team2Inhibitors", "Patch", "LegacyPatch", "PatchSort",
        "MatchHistory", "VOD", "N_Page", "N_MatchInTab", "N_MatchInPage", # Using DB schema names
        "N_GameInMatch", "Gamename", "UniqueLine", "GameId", "MatchId",    # Using DB schema names
        "RiotPlatformGameId", "RiotPlatformId", "RiotGameId", "RiotHash", "RiotVersion"
    ]

    offset = 0
    total_pb_fetched = 0
    total_sg_fetched = 0

    while True:
        print(f"\nFetching ScoreboardGames GameIDs, offset: {offset}")
        sg_query_params = {
            'tables': "ScoreboardGames",
            'fields': "GameId, DateTime_UTC",
            'order_by': "DateTime_UTC DESC",
            'limit': BATCH_SIZE,
            'offset': offset
        }
        if last_timestamp:
            sg_query_params['where'] = f"DateTime_UTC < '{last_timestamp}'"

        # Step 1: Fetch a batch of GameIds from ScoreboardGames, ordered by DateTime_UTC
        print(f"Querying ScoreboardGames refs with params: {sg_query_params}")
        sg_references = site.cargo_client.query(**sg_query_params)

        if not sg_references:
            print("No more ScoreboardGames data to fetch.")
            break

        current_batch_game_ids = list(set([item['GameId'] for item in sg_references if item.get('GameId')]))
        print(f"Fetched {len(sg_references)} ScoreboardGame references, containing {len(current_batch_game_ids)} unique GameIDs.")

        if not current_batch_game_ids:
            print("No GameIDs in current batch from ScoreboardGames, stopping.")
            break

        # Step 2: For these GameIDs, find corresponding PicksAndBansS7 entries (UniqueLine)
        pb_references_for_game_ids = []
        # Further reduced chunk size from 30 to 20 for PB lookup
        game_id_chunks_for_pb_lookup = [current_batch_game_ids[i:i + 20] for i in range(0, len(current_batch_game_ids), 20)]

        for chunk in game_id_chunks_for_pb_lookup:
            if not chunk: continue
            pb_lookup_query_str = f"'{ "','".join(chunk) }'"
            current_pb_query_params = {
                'tables': "PicksAndBansS7",
                'fields': "UniqueLine, GameId",
                'where': f"GameId IN ({pb_lookup_query_str})"
            }
            print(f"Querying PicksAndBansS7 refs with params: {current_pb_query_params}")
            pb_refs = site.cargo_client.query(**current_pb_query_params)
            if pb_refs:
                pb_references_for_game_ids.extend(pb_refs)

        pb_unique_lines_to_fetch = list(set([item['UniqueLine'] for item in pb_references_for_game_ids if item.get('UniqueLine')]))
        # GameIds that actually have a PicksAndBansS7 entry
        game_ids_with_pb_data = list(set([item['GameId'] for item in pb_references_for_game_ids if item.get('GameId')]))

        print(f"Found {len(pb_references_for_game_ids)} PicksAndBansS7 references for these GameIDs, with {len(pb_unique_lines_to_fetch)} unique UniqueLines.")

        if not game_ids_with_pb_data and not pb_unique_lines_to_fetch:
            print("No corresponding PicksAndBansS7 data found for the current batch of GameIDs. Continuing to next SG batch.")
            offset += len(sg_references) # Important: advance offset based on sg_references fetched
            if len(sg_references) < BATCH_SIZE:
                print("Fetched less than BATCH_SIZE from ScoreboardGames, assuming end of data.")
                break
            time.sleep(1)
            continue


        # Step 3. Fetch full ScoreboardGames data for game_ids_with_pb_data (or all current_batch_game_ids if desired, for now only those with PB data)
        sg_data_batch = []
        if game_ids_with_pb_data: # Only fetch SG data if there's corresponding PB data
            game_id_chunks_for_sg_fetch = [game_ids_with_pb_data[i:i + 50] for i in range(0, len(game_ids_with_pb_data), 50)]
            for chunk in game_id_chunks_for_sg_fetch:
                if not chunk: continue
                sg_query_str = f"'{ "','".join(chunk) }'"
                current_sg_fetch_params = {
                    'tables': "ScoreboardGames",
                    'fields': ", ".join(all_sg_fields_list),
                    'where': f"GameId IN ({sg_query_str})"
                }
                print(f"Querying full ScoreboardGames with params: {current_sg_fetch_params}")
                sg_batch_ind = site.cargo_client.query(**current_sg_fetch_params)
                if sg_batch_ind:
                    sg_data_batch.extend(sg_batch_ind)

            if sg_data_batch: # Print keys of the first item if data exists
                print(f"Debug: Keys in received ScoreboardGames data: {list(sg_data_batch[0].keys())}")
                print(f"Debug: Number of keys: {len(list(sg_data_batch[0].keys()))}")
                print(f"Debug: Expected number of columns: {len(all_sg_fields_list)}")


            print(f"Fetched {len(sg_data_batch)} full ScoreboardGames entries.")
            inserted_sg_count = insert_scoreboard_games_batch(sg_data_batch)
            total_sg_fetched += inserted_sg_count
        else:
            print("Skipping ScoreboardGames full data fetch as no corresponding PicksAndBansS7 entries found for this batch.")


        # Step 4. Fetch full PicksAndBansS7 data for pb_unique_lines_to_fetch
        pb_data_batch = []
        if pb_unique_lines_to_fetch:
            pb_unique_line_chunks = [pb_unique_lines_to_fetch[i:i + 50] for i in range(0, len(pb_unique_lines_to_fetch), 50)]
            for chunk in pb_unique_line_chunks:
                if not chunk: continue
                pb_query_str = f"'{ "','".join(chunk) }'"
                pb_batch_ind = site.cargo_client.query(
                    tables="PicksAndBansS7",
                    fields=", ".join(all_pb_fields_list),
                    where=f"UniqueLine IN ({pb_query_str})"
                )
                if pb_batch_ind:
                    pb_data_batch.extend(pb_batch_ind)

            if pb_data_batch: # Debug print for PicksAndBansS7
                print(f"Debug: Keys in received PicksAndBansS7 data: {list(pb_data_batch[0].keys())}")
                print(f"Debug: Number of keys in PB data: {len(list(pb_data_batch[0].keys()))}")
                print(f"Debug: Expected number of PB columns: {len(all_pb_fields_list)}")


            print(f"Fetched {len(pb_data_batch)} full PicksAndBansS7 entries.")
            inserted_pb_count = insert_picks_and_bans_batch(pb_data_batch)
            total_pb_fetched += inserted_pb_count
        else:
            print("Skipping PicksAndBansS7 full data fetch as no UniqueLines were identified for this batch.")


        # Advance offset based on the number of ScoreboardGames references fetched initially
        offset += len(sg_references)

        if len(sg_references) < BATCH_SIZE:
            print("Fetched less than BATCH_SIZE from ScoreboardGames, assuming end of data for current criteria.")
            break

        print("Waiting 10 seconds to respect API rate limits...")
        time.sleep(10) # Be polite to the API

    print(f"\nData collection complete. Total new ScoreboardGames rows: {total_sg_fetched}, Total new PicksAndBansS7 rows: {total_pb_fetched}")

if __name__ == '__main__':
    # Ensure tables exist
    from . import db_setup
    db_setup.create_tables()

    collect_data()
