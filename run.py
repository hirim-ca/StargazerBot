import os
from configparser import ConfigParser
from stargazerBot import StargazerBot

from db import PostgreSQL

def run():
    config = ConfigParser()
    config.read("config.ini")
    keys = ConfigParser()
    keys.read("keys.ini")


    db = PostgreSQL(
        user = keys.get("DB", "DB_USER"),
        password = keys.get("DB", "DB_PASSWORD"),
        host = keys.get("DB", "HOST"),
        port = keys.get("DB", "PORT"),
        database = keys.get("DB", "DB_NAME")
    )

    stargazerBot = StargazerBot(
        db = db, 
        name = config.get("BOT", "NAME"),
        owner_id = int(keys.get("BOT", "OWNER_ID")),
        ext_path = config.get("BOT", "EXTENTION_PATH"),
        output_path = config.get("BOT", "OUTPUT_PATH"),
        command_prefix=config.get("BOT", "COMMAND_PREFIX")
    )

    stargazerBot.run(keys.get("BOT", "TOKEN"))

if __name__ == "__main__":
    run()