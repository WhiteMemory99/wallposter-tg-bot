from app.models.base import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, index=True)


class UserRelatedModel(db.Model):
    __abstract__ = True

    user_id = db.Column(db.ForeignKey(f"{User.__tablename__}.id", ondelete="CASCADE", onupdate="CASCADE"))
