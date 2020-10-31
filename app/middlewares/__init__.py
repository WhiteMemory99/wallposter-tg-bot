from aiogram import Dispatcher

from app.middlewares.acl import ACLMiddleware


def setup(dispatcher: Dispatcher):
    dispatcher.middleware.setup(ACLMiddleware())
