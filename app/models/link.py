from app.models.base import db
from app.models.channel import ChannelRelatedModel
from app.models.user import UserRelatedModel


class Link(UserRelatedModel, ChannelRelatedModel):
    __tablename__ = "channel_link"

    id = db.Column(db.BigInteger, primary_key=True, index=True)
