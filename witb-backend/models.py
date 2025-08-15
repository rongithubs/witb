import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Player(Base):
    __tablename__ = "players"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    country = Column(String)
    tour = Column(String)
    age = Column(Integer)
    ranking = Column(Integer)
    photo_url = Column(String)
    last_updated = Column(
        DateTime, default=func.now()
    )  # Only set on creation, WITB scraper will update manually
    witb_items = relationship("WITBItem", back_populates="player", lazy="selectin")


class WITBItem(Base):
    __tablename__ = "witb_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"))
    category = Column(String)
    brand = Column(String)
    model = Column(String)
    loft = Column(String)
    shaft = Column(String)
    product_url = Column(String)
    source_url = Column(String, nullable=True)
    last_updated = Column(DateTime, default=func.now())
    player = relationship("Player", back_populates="witb_items")


class SystemUpdate(Base):
    __tablename__ = "system_updates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    update_type = Column(String, nullable=False)  # "owgr", "witb", etc.
    last_updated = Column(DateTime, default=func.now())
    details = Column(String, nullable=True)  # JSON string with update details
