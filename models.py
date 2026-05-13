from sqlalchemy import Column, Integer, String
from database import Base


# =========================
# USER TABLE
# =========================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String,
        unique=True,
        index=True
    )

    password = Column(
        String
    )


# =========================
# FOOD TABLE
# =========================

class Food(Base):

    __tablename__ = "foods"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    donor = Column(String)

    food = Column(String)

    quantity = Column(Integer)

    location = Column(String)

    phone = Column(String)

    status = Column(String)