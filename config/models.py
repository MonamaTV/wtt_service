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
    Column("users", ForeignKey("users.id"), primary_key=True),
    Column("competitions", ForeignKey("competitions.id"), primary_key=True),
    Column("score_id", String)
)


class Competition(Base):
    __tablename__ = "competitions"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid4())
    creator_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    name: Mapped[Optional[str]]
    created_at: Mapped[Optional[date]] = mapped_column(default=datetime.now())
    expires_in: Mapped[date]
    users: Mapped[List["User"]] = relationship(
        secondary=association_table, back_populates="competitions"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid4())
    email: Mapped[str] = mapped_column()
    first_name: Mapped[Optional[str]]
    last_name: Mapped[Optional[str]]
    password: Mapped[str]
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[date] = mapped_column(default=datetime.now())

    # Relationships
    scores: Mapped[List["Score"]] = relationship(back_populates="user")
    competitions: Mapped[List["Competition"]] = relationship(
        secondary=association_table, back_populates="users"
    )


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    wpm: Mapped[float]
    played_at: Mapped[Optional[date]] = mapped_column(default=datetime.now())
    words: Mapped[int]
    accuracy: Mapped[float]
    duration: Mapped[time]
    characters: Mapped[int]
    completed: Mapped[bool]

    # Relationship
    user: Mapped["User"] = relationship(back_populates="scores")


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
