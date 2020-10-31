from app.models.base import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, index=True)
    chat_id = db.Column(db.BigInteger, default=None)
    enable_sign = db.Column(db.Boolean, default=True)
    sign_text = db.Column(db.String(250), default=None)
    enable_counter = db.Column(db.Boolean, default=True)
    counter = db.Column(db.Integer, default=0)
    scheduler_hours = db.Column(db.Integer, default=3)


class UserRelatedModel(db.Model):
    __abstract__ = True

    user_id = db.Column(db.ForeignKey(f'{User.__tablename__}.id', ondelete='CASCADE', onupdate='CASCADE'))
