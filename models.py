from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Sighting(Base):
    __tablename__ = "tick_sightings"
    __table_args__ = (
        UniqueConstraint("date", "location", "species", name="unique_tick_sightings"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    date: Mapped[str] = mapped_column(String, index=True, nullable=False)
    location: Mapped[str] = mapped_column(String, index=True, nullable=False)
    species: Mapped[str] = mapped_column(String, index=True, nullable=False)
    latin_name: Mapped[str] = mapped_column(String,index=True, nullable=False)

