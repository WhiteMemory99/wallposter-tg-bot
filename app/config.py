from envparse import env


env.read_envfile()

BOT_TOKEN = env.str('BOT_TOKEN')

REDIS_HOST = env.str('REDIS_HOST', default='localhost')
REDIS_PASSWORD = env.str('REDIS_PASSWORD')

POSTGRES_HOST = env.str('POSTGRES_HOST', default='localhost')
POSTGRES_USER = env.str('POSTGRES_USER')
POSTGRES_PASSWORD = env.str('POSTGRES_PASSWORD')
DB_NAME = env.str('DB_NAME')
DB_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{DB_NAME}'
