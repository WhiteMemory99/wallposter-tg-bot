from app.models.base import db
from app.models.channel import Channel
from app.models.link import Link
from app.models.user import User
from app.models.wallpaper import Wallpaper


async def setup(database_path: str):
    await db.set_bind(database_path)


async def shutdown():
    bind = db.pop_bind()
    if bind:
        await bind.close()


__all__ = ("db", "User", "Channel", "Wallpaper", "Link")
