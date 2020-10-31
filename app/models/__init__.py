from app.models.base import db
from app.models.wallpaper import Wallpaper
from app.models.user import User


async def setup(database_path: str):
    await db.set_bind(database_path)


async def shutdown():
    bind = db.pop_bind()
    if bind:
        await bind.close()


__all__ = (
    'db',
    'User',
    'Wallpaper'
)
