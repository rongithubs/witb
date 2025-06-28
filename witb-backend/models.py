from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
import uuid

Base = declarative_base()

class Player(Base):
    __tablename__ = "players"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    country = Column(String)
    tour = Column(String)
    age = Column(Integer)
    photo_url = Column(String)
    witb_items = relationship(
        "WITBItem", back_populates="player", lazy="selectin"
    )


class WITBItem(Base):
    __tablename__ = "witb_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = Column(UUID(as_uuid=True), ForeignKey("players.id"))
    category = Column(String)
    brand = Column(String)
    model = Column(String)
    loft = Column(String)
    shaft = Column(String)
    player = relationship("Player", back_populates="witb_items")
