from sqlalchemy import Column, Integer, ForeignKey, text
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.sql.sqltypes import TIMESTAMP, VARCHAR

from .db.base import Base


class User(Base):
    __tablename__ = "User"

    user_id = Column(Integer, primary_key=True, nullable=False)
    nickname = Column(VARCHAR(25), unique=True, nullable=False)
    email = Column(VARCHAR(40), unique=True, nullable=False)
    password = Column(VARCHAR(50), nullable=False)
    registered_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=text('now()'))


class Song(Base):
    __tablename__ = "Song"

    song_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(50), nullable=False)
    author = Column(VARCHAR(50), nullable=False)
    track = Column(BYTEA, nullable=False)
    uploaded_at = Column(TIMESTAMP(timezone=False), nullable=False, server_default=text('now()'))


class LikedSongs(Base):
    __tablename__ = "Liked_Songs"

    user_id = Column(Integer, ForeignKey("User.user_id", ondelete="CASCADE"), primary_key=True, nullable=False)
    song_id = Column(Integer, ForeignKey("Song.song_id", ondelete="CASCADE"), primary_key=True, nullable=False)
