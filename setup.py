import sqlite3
import shutil
from os.path import isfile


DB_DIR = './line.db'
CONF_TEMPLATE_DIR = './src/template_conf.toml'
CONF_DIR = './bot_conf.toml'


def main() -> None:
    if isfile(DB_DIR):
        print('The database already exists, skipping...')
    else:
        make_db()

    if isfile(CONF_DIR):
        print('The configuration file already exists, skipping...')
    else:
        make_conf()

    print('The bot is setup and ready to use!')


def make_db() -> None:
    conn = sqlite3.connect(DB_DIR)
    cursor = conn.cursor()
    print(f'Connected to database at "{DB_DIR}"')

    cursor.execute(
        """--sql
            CREATE TABLE "blacklist" (
                "user" INTEGER PRIMARY KEY
            );
        """
    )
    print('Table "blacklist" created')

    cursor.execute(
        """--sql
            CREATE TABLE "changelog" (
                "version" TEXT PRIMARY KEY,
                "date" TEXT DEFAULT '?',
                "content" TEXT,
                "hidden" INTEGER DEFAULT 1
            );
        """
    )
    print('Table "changelog" created')

    cursor.execute(
        """--sql
            CREATE TABLE "colors" (
                "id" INTEGER PRIMARY KEY,
                "value" INTEGER
            );
        """
    )
    print('Table "colors" created')

    cursor.execute(
        """--sql
            CREATE TABLE "commandstats" (
                "command" TEXT PRIMARY KEY,
                "uses" INTEGER NOT NULL DEFAULT 1
            );
        """
    )
    print('Table "commandstats" created')

    cursor.execute(
        """--sql
            CREATE TABLE "tags" (
                "guild" INTEGER NOT NULL,
                "user" INTEGER NOT NULL,
                "name" TEXT NOT NULL,
                "content" TEXT NOT NULL,
                "nsfw" INTEGER NOT NULL,
                PRIMARY KEY("guild", "name")
            );
        """
    )
    print('Table "tags" created')

    cursor.execute(
        """--sql
            CREATE TABLE "tagsenabled" (
                "guild" INTEGER PRIMARY KEY
            );
        """
    )
    print('Table "tagsenabled" created')
    conn.commit()
    conn.close()

    print('Successfully created the database tables')


def make_conf() -> None:
    try:
        shutil.copy(CONF_TEMPLATE_DIR, CONF_DIR)
    except IOError:
        print('An error ocurred: The destination location is not writable')
        exit(1)

    print(f'A config file was generated for you at "{CONF_DIR}"')
    print('Now you should put your app\'s token(s) in the [token] table of your TOML config file')


if __name__ == '__main__':
    main()
