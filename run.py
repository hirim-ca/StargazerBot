import os
from configparser import ConfigParser
from stargazerBot import StargazerBot

from db import PostgreSQL

def run():
    config = ConfigParser()
    config.read("config.ini")

    if (int(config.get("BOT", "LOCAL"))):
        keys = ConfigParser()
        keys.read("key.ini")
        db_user = keys.get("KEYS", "DB_USER")
        db_name = keys.get("KEYS", "DB_NAME")
        db_password = keys.get("KEYS", "DB_PASSWORD")
        token = keys.get("KEYS", "TOKEN")
    else:
        db_user = os.getenv("DB_USER")
        db_name = os.getenv("DB_NAME")
        db_password = os.getenv("DB_PASSWORD")
        token = os.getenv("TOKEN")

    db = PostgreSQL(
        user = db_user,
        password = db_password,
        host = config.get("DB", "HOST"),
        port = config.get("DB", "PORT"),
        database = db_name
    )

    stargazerBot = StargazerBot(
        db = db, 
        owner_id = int(config.get("BOT", "OWNER_ID")),
        ext_path = config.get("BOT", "EXTENTION_PATH"),
        output_path = config.get("BOT", "OUTPUT_PATH"),
        command_prefix=config.get("BOT", "COMMAND_PREFIX")
    )

    stargazerBot.run(token)

if __name__ == "__main__":
    run()