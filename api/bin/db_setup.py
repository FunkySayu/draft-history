import sqlite3

DB_NAME = 'league_data.db'

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ScoreboardGames Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ScoreboardGames (
        OverviewPage TEXT,
        Tournament TEXT,
        Team1 TEXT,
        Team2 TEXT,
        WinTeam TEXT,
        LossTeam TEXT,
        DateTime_UTC TEXT,
        DST TEXT,
        Team1Score INTEGER,
        Team2Score INTEGER,
        Winner INTEGER,
        Gamelength TEXT,
        Gamelength_Number REAL,
        Team1Bans TEXT,
        Team2Bans TEXT,
        Team1Picks TEXT,
        Team2Picks TEXT,
        Team1Players TEXT,
        Team2Players TEXT,
        Team1Dragons INTEGER,
        Team2Dragons INTEGER,
        Team1Barons INTEGER,
        Team2Barons INTEGER,
        Team1Towers INTEGER,
        Team2Towers INTEGER,
        Team1Gold REAL,
        Team2Gold REAL,
        Team1Kills INTEGER,
        Team2Kills INTEGER,
        Team1RiftHeralds INTEGER,
        Team2RiftHeralds INTEGER,
        Team1VoidGrubs INTEGER,
        Team2VoidGrubs INTEGER,
        Team1Atakhans INTEGER,
        Team2Atakhans INTEGER,
        Team1Inhibitors INTEGER,
        Team2Inhibitors INTEGER,
        Patch TEXT,
        LegacyPatch TEXT,
        PatchSort TEXT,
        MatchHistory TEXT,
        VOD TEXT,
        N_Page INTEGER,
        N_MatchInTab INTEGER,
        N_MatchInPage INTEGER,
        N_GameInMatch INTEGER,
        Gamename TEXT,
        UniqueLine TEXT,
        GameId TEXT PRIMARY KEY,
        MatchId TEXT,
        RiotPlatformGameId TEXT,
        RiotPlatformId TEXT,
        RiotGameId TEXT,
        RiotHash TEXT,
        RiotVersion INTEGER
    )
    ''')

    # PicksAndBansS7 Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PicksAndBansS7 (
        Team1Role1 TEXT,
        Team1Role2 TEXT,
        Team1Role3 TEXT,
        Team1Role4 TEXT,
        Team1Role5 TEXT,
        Team2Role1 TEXT,
        Team2Role2 TEXT,
        Team2Role3 TEXT,
        Team2Role4 TEXT,
        Team2Role5 TEXT,
        Team1Ban1 TEXT,
        Team1Ban2 TEXT,
        Team1Ban3 TEXT,
        Team1Ban4 TEXT,
        Team1Ban5 TEXT,
        Team1Pick1 TEXT,
        Team1Pick2 TEXT,
        Team1Pick3 TEXT,
        Team1Pick4 TEXT,
        Team1Pick5 TEXT,
        Team2Ban1 TEXT,
        Team2Ban2 TEXT,
        Team2Ban3 TEXT,
        Team2Ban4 TEXT,
        Team2Ban5 TEXT,
        Team2Pick1 TEXT,
        Team2Pick2 TEXT,
        Team2Pick3 TEXT,
        Team2Pick4 TEXT,
        Team2Pick5 TEXT,
        Team1 TEXT,
        Team2 TEXT,
        Winner INTEGER,
        Team1Score INTEGER,
        Team2Score INTEGER,
        Team1PicksByRoleOrder TEXT,
        Team2PicksByRoleOrder TEXT,
        OverviewPage TEXT,
        Phase TEXT,
        UniqueLine TEXT PRIMARY KEY,
        IsComplete INTEGER,
        IsFilled INTEGER,
        Tab TEXT,
        N_Page INTEGER,
        N_TabInPage INTEGER,
        N_MatchInPage INTEGER,
        N_GameInPage INTEGER,
        N_GameInMatch INTEGER,
        N_MatchInTab INTEGER,
        N_GameInTab INTEGER,
        GameId TEXT,
        MatchId TEXT,
        GameID_Wiki TEXT,
        FOREIGN KEY (GameId) REFERENCES ScoreboardGames(GameId)
    )
    ''')

    conn.commit()
    conn.close()
    print(f"Tables created successfully in {DB_NAME}.")

if __name__ == '__main__':
    create_tables()
