import sqlite3


FILE_DIR = './line.db'


def main() -> None:
    conn = sqlite3.connect(FILE_DIR)
    cursor = conn.cursor()

    cursor.execute(
        """--sql
            CREATE TABLE "BLACKLIST" (
                "USER" INTEGER,
                PRIMARY KEY("USER")
            )
        """
    )

    cursor.execute(
        """--sql
            CREATE TABLE "CHANGELOG" (
                "VERSION" TEXT UNIQUE,
                "DATE" TEXT DEFAULT '?',
                "CONTENT" INTEGER,
                "HIDDEN" INTEGER DEFAULT 1,
                PRIMARY KEY("VERSION")
            )               
        """
    )

    cursor.execute(
        """--sql
            CREATE TABLE "COLORS" (
                "ID" INTEGER UNIQUE,
                "VALUE" INTEGER,
                PRIMARY KEY("ID")
            )
        """
    )

    cursor.execute(
        """--sql
            CREATE TABLE "COMMANDSTATS" (
                "COMMAND" TEXT,
                "USES" INTEGER DEFAULT 1,
                PRIMARY KEY("COMMAND")
            )
        """
    )

    cursor.execute(
        """--sql
            CREATE TABLE "RESOURCES" (
                "KEY" TEXT UNIQUE,
                "VALUE" TEXT,
                PRIMARY KEY("KEY")
            )
        """
    )

    cursor.execute(
        """--sql
            CREATE TABLE "TAGS" (
                "GUILD" INTEGER,
                "USER" INTEGER,
                "NAME" TEXT,
                "CONTENT" TEXT,
                "NSFW" INTEGER
            )
        """
    )

    cursor.execute(
        """--sql
            CREATE TABLE "TAGSENABLED" (
                "GUILD" INTEGER,
                PRIMARY KEY("GUILD")
            )
        """
    )


if __name__ == '__main__':
    main()
