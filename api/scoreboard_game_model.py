from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import relationship # Import relationship
from .models_base import Base

class ScoreboardGame(Base):
    __tablename__ = "ScoreboardGames"

    # ... existing columns ...

    OverviewPage = Column(Text)
    Tournament = Column(Text)
    Team1 = Column(Text)
    Team2 = Column(Text)
    WinTeam = Column(Text)
    LossTeam = Column(Text)
    DateTime_UTC = Column(Text) # Store as ISO8601 string
    DST = Column(Text)
    Team1Score = Column(Integer)
    Team2Score = Column(Integer)
    Winner = Column(Integer) # 1 for Team1, 2 for Team2, 0 for TBD/Tie (assumption)
    Gamelength = Column(Text) # e.g., "30:45"
    Gamelength_Number = Column(Float) # e.g., 30.75 (minutes)
    Team1Bans = Column(Text) # Comma-separated list
    Team2Bans = Column(Text) # Comma-separated list
    Team1Picks = Column(Text) # Comma-separated list
    Team2Picks = Column(Text) # Comma-separated list
    Team1Players = Column(Text) # Comma-separated list
    Team2Players = Column(Text) # Comma-separated list
    Team1Dragons = Column(Integer)
    Team2Dragons = Column(Integer)
    Team1Barons = Column(Integer)
    Team2Barons = Column(Integer)
    Team1Towers = Column(Integer)
    Team2Towers = Column(Integer)
    Team1Gold = Column(Float)
    Team2Gold = Column(Float)
    Team1Kills = Column(Integer)
    Team2Kills = Column(Integer)
    Team1RiftHeralds = Column(Integer)
    Team2RiftHeralds = Column(Integer)
    Team1VoidGrubs = Column(Integer)
    Team2VoidGrubs = Column(Integer)
    Team1Atakhans = Column(Integer) # Assuming this is an objective/event count
    Team2Atakhans = Column(Integer)
    Team1Inhibitors = Column(Integer)
    Team2Inhibitors = Column(Integer)
    Patch = Column(Text)
    LegacyPatch = Column(Text) # Assuming this is different from Patch
    PatchSort = Column(Text) # For sorting patches if Patch itself isn't sortable
    MatchHistory = Column(Text) # URL or reference
    VOD = Column(Text) # Wikitext, could be complex
    N_Page = Column(Integer)
    N_MatchInTab = Column(Integer)
    N_MatchInPage = Column(Integer)
    N_GameInMatch = Column(Integer)
    Gamename = Column(Text)
    UniqueLine = Column(Text) # This might be an alternative key from API, but GameId is primary for this table
    GameId = Column(String, primary_key=True) # Leaguepedia GameId
    MatchId = Column(String) # Leaguepedia MatchId
    RiotPlatformGameId = Column(Text)
    RiotPlatformId = Column(Text)
    RiotGameId = Column(Text) # Riot's Game ID, may differ from RiotPlatformGameId
    RiotHash = Column(Text)
    RiotVersion = Column(Integer)

    # Relationship to PicksAndBansS7Model
    picks_and_bans = relationship("PicksAndBansS7Model", back_populates="scoreboard_game")

    def __repr__(self):
        return f"<ScoreboardGame(GameId='{self.GameId}', Tournament='{self.Tournament}', Team1='{self.Team1}', Team2='{self.Team2}')>"
