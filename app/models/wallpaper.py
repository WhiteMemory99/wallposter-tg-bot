from app.models.base import db
from app.models.channel import ChannelRelatedModel
from app.models.user import UserRelatedModel


class Wallpaper(ChannelRelatedModel, UserRelatedModel):
    __tablename__ = "wallpapers"

    id = db.Column(db.BigInteger, primary_key=True, index=True)
    file_id = db.Column(db.String(100), nullable=False)
    unique_file_id = db.Column(db.String(100), nullable=False)
    extension = db.Column(db.String(10), default="jpeg")
    custom_signature = db.Column(db.String(250), default=None)
    telegraph_link = db.Column(db.String(100), default=None)
