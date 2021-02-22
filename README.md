# Wallposter Telegram Bot

Backend of [@wallposter_bot](https://t.me/wallposter_bot) - a cool telegram bot for posting user wallpapers into their
channels. It uses Redis, PostgreSQL and based on aiogram.

## Setting up

### Poetry

**_Make sure you have installed [poetry](https://python-poetry.org/docs/)._**

1. Git clone this repo and go to its dir

   ```cmd
   git clone https://github.com/WhiteMemory99/wallposter-tg-bot.git; cd wallposter-tg-bot
   ```

2. Rename `.env.dist` to `.env` and fill in your Redis, Postgres credentials and your bot token.
3. Install requirements

   ```cmd
   poetry install
   ```

4. Apply alembic migrations

   ```cmd
   poetry run alembic upgrade head
   ```

5. Run the script with poetry

   ```cmd
   poetry run python app
   ```
