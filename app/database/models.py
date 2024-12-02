from tkinter.tix import COLUMN, INTEGER

from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import sql

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
async_session = async_sessionmaker(engine)
class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[BigInteger] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column()
    age: Mapped[int] = mapped_column()
    whuare: Mapped[str] = mapped_column()
    number: Mapped[str] = mapped_column(String(25))
    count_otvet: Mapped[int] = mapped_column()
    count_otvet_x: Mapped[float] = mapped_column()
    premium: Mapped[str] = mapped_column()
    balls: Mapped[int] = mapped_column()
    balls_x: Mapped[float] = mapped_column()
    solved_tasks: Mapped[int] = mapped_column()
    level: Mapped[int] = mapped_column()
    balance: Mapped[int] = mapped_column()





class Materialcat(Base):
    __tablename__ = 'materialcats'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

class Material(Base):
    __tablename__ = 'materials'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(25))
    description: Mapped[str] = mapped_column(String(50))
    materialcat: Mapped[int] = mapped_column(ForeignKey('materialcats.id'))

class Photomat(Base):
    __tablename__ = 'photos'
    id: Mapped[int] = mapped_column(primary_key=True)
    photo: Mapped[str] = mapped_column(String(50))
    answer: Mapped[str] = mapped_column(String(50))
    material: Mapped[int] = mapped_column(ForeignKey('materials.id'))
    materialcat: Mapped[int] = mapped_column(ForeignKey('materialcats.id'))

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

