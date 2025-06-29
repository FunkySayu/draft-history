from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .models_base import Base

class PicksAndBansS7Model(Base):
    __tablename__ = "PicksAndBansS7"

    Team1Role1 = Column(String)
    Team1Role2 = Column(String)
    Team1Role3 = Column(String)
    Team1Role4 = Column(String)
    Team1Role5 = Column(String)
    Team2Role1 = Column(String)
    Team2Role2 = Column(String)
    Team2Role3 = Column(String)
    Team2Role4 = Column(String)
    Team2Role5 = Column(String)
    Team1Ban1 = Column(String)
    Team1Ban2 = Column(String)
    Team1Ban3 = Column(String)
    Team1Ban4 = Column(String)
    Team1Ban5 = Column(String)
    Team1Pick1 = Column(String)
    Team1Pick2 = Column(String)
    Team1Pick3 = Column(String)
    Team1Pick4 = Column(String)
    Team1Pick5 = Column(String)
    Team2Ban1 = Column(String)
    Team2Ban2 = Column(String)
    Team2Ban3 = Column(String)
    Team2Ban4 = Column(String)
    Team2Ban5 = Column(String)
    Team2Pick1 = Column(String)
    Team2Pick2 = Column(String)
    Team2Pick3 = Column(String)
    Team2Pick4 = Column(String)
    Team2Pick5 = Column(String)
    Team1 = Column(String)
    Team2 = Column(String)
    Winner = Column(Integer) # 1 for Team1, 2 for Team2
    Team1Score = Column(Integer)
    Team2Score = Column(Integer)
    Team1PicksByRoleOrder = Column(Text) # Could be comma-separated or JSON
    Team2PicksByRoleOrder = Column(Text) # Could be comma-separated or JSON
    OverviewPage = Column(String)
    Phase = Column(String) # e.g., "Draft", "Game" - though S7 implies draft
    UniqueLine = Column(String, primary_key=True) # Unique identifier for this pick/ban entry
    IsComplete = Column(Boolean) # Or Integer if SQLite handles Boolean as 0/1
    IsFilled = Column(Boolean)   # Or Integer
    Tab = Column(String)
    N_Page = Column(Integer)
    N_TabInPage = Column(Integer)
    N_MatchInPage = Column(Integer)
    N_GameInPage = Column(Integer)
    N_GameInMatch = Column(Integer)
    N_MatchInTab = Column(Integer)
    N_GameInTab = Column(Integer)

    GameId = Column(String, ForeignKey("ScoreboardGames.GameId"))
    MatchId = Column(String)
    GameID_Wiki = Column(String) # Wiki-specific Game ID, if different

    # Define the relationship to ScoreboardGame
    scoreboard_game = relationship("ScoreboardGame", back_populates="picks_and_bans")

    def __repr__(self):
        return f"<PicksAndBansS7Model(UniqueLine='{self.UniqueLine}', GameId='{self.GameId}')>"
