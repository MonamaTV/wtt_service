from sqlalchemy import ForeignKey, Table, Column, String
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date, time, datetime
from uuid import UUID, uuid4
from sqlalchemy.orm import DeclarativeBase, relationship
from typing import Optional, List


class Base(DeclarativeBase):
    pass


association_table = Table(
    "competition_user_mapping",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("competition_id", ForeignKey("competitions.id", ondelete="CASCADE"), primary_key=True),
    Column("score_id", ForeignKey("scores.id"), nullable=True),
)


class CompetitionUserMapping(Base):
    __tablename__ = 'competition_user_mapping'
    __table_args__ = {'extend_existing': True}

    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'), primary_key=True)
    competition_id: Mapped[UUID] = mapped_column(ForeignKey('competitions.id'), primary_key=True)
    score_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('scores.id'), nullable=True)
    # #
    user: Mapped["User"] = relationship(back_populates="user", viewonly=True)
    # competition_details: Mapped["Competition"] = relationship(back_populates="competition_details")
    score: Mapped["Score"] = relationship(back_populates="score")


class Competition(Base):
    __tablename__ = "competitions"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid4())
    creator_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    # winner: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    name: Mapped[Optional[str]]
    created_at: Mapped[Optional[date]] = mapped_column(default=datetime.now())
    expires_in: Mapped[date]
    users: Mapped[List["User"]] = relationship(
        secondary=association_table, back_populates="competitions",
        passive_deletes=True,
    )

    # Relationship
    user: Mapped["User"] = relationship(back_populates="competitions")
    # competition_details: Mapped["CompetitionUserMapping"] = relationship(back_populates="competition_info")
    # comp: Mapped["CompetitionUserMapping"] = relationship("user")


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True)
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    password: Mapped[str]
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[date] = mapped_column(default=datetime.now())
    verified: Mapped[bool] = mapped_column(default=False)
    bio: Mapped[Optional[str]]
    # Relationships
    scores: Mapped[List["Score"]] = relationship(back_populates="user")
    competition_list: Mapped[List["Competition"]] = relationship(back_populates="user")
    # in_competition: Mapped["CompetitionUserMapping"] = relationship(back_populates="in_competition")
    competitions: Mapped[List["Competition"]] = relationship(
        secondary=association_table, back_populates="users",
        cascade="all, delete",
    )
    user: Mapped["CompetitionUserMapping"] = relationship(back_populates="user")


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    wpm: Mapped[float]
    played_at: Mapped[Optional[date]] = mapped_column(default=datetime.now())
    words: Mapped[int]
    accuracy: Mapped[float]
    duration: Mapped[int]
    characters: Mapped[int]
    completed: Mapped[bool]

    # Relationship
    user: Mapped["User"] = relationship(back_populates="scores")
    score: Mapped["CompetitionUserMapping"] = relationship(back_populates="score")


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    difficulty_level: Mapped[str]
    theme: Mapped[str]


class Leaderboard(Base):
    __tablename__ = "leaderboard"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    score: Mapped[int]
    accuracy: Mapped[float]
    # More to come in here
