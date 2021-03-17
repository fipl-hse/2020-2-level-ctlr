"""
Database model for storing parsed articles
"""

from sqlalchemy import create_engine, Column, Table, ForeignKey, Unicode
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, DateTime, UnicodeText

from constants import DB_CONNECTION

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(DB_CONNECTION)


def create_table(engine):
    Base.metadata.create_all(engine)


meta_topic = Table(
    "meta_topic",
    Base.metadata,
    Column("meta_id", Integer, ForeignKey("meta.id")),
    Column("topic.id", Integer, ForeignKey("topic.id")),
)


class Post(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "post"

    id = Column(Integer, ForeignKey("meta.id"), primary_key=True)
    title = Column("title", Unicode(100), nullable=False)
    text = Column("content", UnicodeText(), nullable=False)

    meta = relationship("Meta", backref=backref("meta", uselist=False))


class Meta(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "meta"

    id = Column(Integer, primary_key=True)
    url = Column("url", String(80), nullable=False, unique=True)
    date = Column("date", DateTime())
    author = Column("author", Unicode(40))

    topics = relationship(
        "Topic", secondary="meta_topic", lazy="dynamic", backref="meta"
    )


class Topic(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "topic"

    id = Column(Integer, primary_key=True)
    name = Column("name", Unicode(100), unique=True)
