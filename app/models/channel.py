from sqlalchemy.sql import expression

from app.models.user import db


class Channel(db.Model):
    __tablename__ = "channels"

    id = db.Column(db.BigInteger, primary_key=True, index=True)
    enable_signature = db.Column(db.Boolean, default=True, server_default=expression.true())
    signature_text = db.Column(db.String(250), default=None)
    enable_counter = db.Column(db.Boolean, default=True, server_default=expression.true())
    counter_value = db.Column(db.Integer, default=0)
    scheduler_hours = db.Column(db.Integer, default=3)


class ChannelRelatedModel(db.Model):
    __abstract__ = True

    channel_id = db.Column(db.ForeignKey(f"{Channel.__tablename__}.id", ondelete="CASCADE", onupdate="CASCADE"))
