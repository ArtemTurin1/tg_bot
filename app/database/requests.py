from collections import Counter
from operator import itemgetter

from app.database.models import async_session
from app.database.models import User,Material,Materialcat, Photomat
from sqlalchemy import select
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id = tg_id))
            await session.commit()

async def get_materialcategoriis():
    async with async_session() as session:
        return await session.scalars(select(Materialcat))

async def get_materialcategoriis_item(materialcat_id):
    async with async_session() as session:
        return await session.scalars(select(Material).where(Material.materialcat == materialcat_id))

async def get_material(material_id):
    async with async_session() as session:
        return await session.scalar(select(Material).where(Material.id == material_id))

async def get_photo(photo_id):
    async with async_session() as session:
        return  await session.scalars(select(Photomat).where(Photomat.material == photo_id))

async def get_liders():
    async with async_session() as session:
        result = await session.execute(select(User.name, User.solved_tasks).where(User.solved_tasks != 0))
        users = result.all()
        top_users = {}
        for name, balls in users:
            top_users[name] = balls
        sorted_users = sorted(top_users.items(), key=lambda item: item[1], reverse=True)
        return sorted_users




async def get_users(name):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.name == name))

