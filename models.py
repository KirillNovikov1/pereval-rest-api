from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, Float, ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

STATUS_VALUES = ("new", "pending", "accepted", "rejected")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String)
    fam = Column(String)
    name = Column(String)
    otc = Column(String)


class Coord(Base):
    __tablename__ = "coords"

    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    height = Column(Integer, nullable=False)


class Pereval(Base):
    __tablename__ = "pereval_added"
    __table_args__ = (
        CheckConstraint(
            "status IN ('new', 'pending', 'accepted', 'rejected')",
            name="check_pereval_status",
        ),
    )

    id = Column(Integer, primary_key=True)
    beautyTitle = Column(String, nullable=False)
    title = Column(String, nullable=False)
    other_titles = Column(String)
    connect = Column(String)
    add_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    coord_id = Column(Integer, ForeignKey("coords.id"), nullable=False)
    winter_level = Column(String)
    summer_level = Column(String)
    autumn_level = Column(String)
    spring_level = Column(String)
    status = Column(String, nullable=False, default="new")

    user = relationship("User")
    coord = relationship("Coord")
    images = relationship("PerevalImage", cascade="all, delete-orphan")


class PerevalImage(Base):
    __tablename__ = "pereval_images"

    id = Column(Integer, primary_key=True)
    pereval_id = Column(Integer, ForeignKey("pereval_added.id"), nullable=False)
    title = Column(String)
    img = Column(LargeBinary)
    date_added = Column(DateTime, default=datetime.utcnow, nullable=False)
