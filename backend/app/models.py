"""SQLAlchemy ORM models."""
from __future__ import annotations

import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text

from app.db import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    rss_url = Column(String, nullable=True)
    category = Column(String, nullable=False)
    type = Column(String, nullable=False)
    language = Column(String, default="en")
    weight = Column(Float, default=1.0)


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String, ForeignKey("sources.id"), nullable=False, index=True)
    url = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=True)
    published_at = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, default=datetime.datetime.utcnow)
    raw_excerpt = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    score = Column(Float, default=0.0)
    selected_for_today = Column(Boolean, default=False)
    day = Column(Date, nullable=True, index=True)


class CustomSource(Base):
    __tablename__ = "custom_sources"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    rss_url = Column(String, nullable=True)
    category = Column(String, default="custom")
    type = Column(String, default="blog")
    language = Column(String, default="en")
    weight = Column(Float, default=1.2)
    active = Column(Boolean, default=True)
    added_at = Column(DateTime, default=datetime.datetime.utcnow)


class SourceOverride(Base):
    __tablename__ = "source_overrides"

    source_id = Column(String, primary_key=True)
    active = Column(Boolean, default=True)
    weight_override = Column(Float, nullable=True)
