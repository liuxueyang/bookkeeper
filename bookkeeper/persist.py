# encoding: utf-8
""" Small database wrapper allowing install management.

This allows bookkeeper to keep track of which is installed (and where).
"""
import os
import sqlite3

DB_FILE = '~/.bookkeeper.db'


class DB(object):

    """ Manages the sqlite connection. """

    _instance = None

    @classmethod
    def get_instance(cls):
        """ Singleton instance. """
        if DB._instance is None:
            DB._instance = cls()
        return DB._instance

    @classmethod
    def set_verbose(cls, verbose):
        """ Toggle verbosity. """
        cls.get_instance().verbose = verbose

    def __init__(self, verbose=False):
        """ Create sqlite connection. """
        self.path = (
            os.path.expandvars(DB_FILE)
            if '$' in DB_FILE else
            os.path.expanduser(DB_FILE)
        )
        self.verbose = verbose

    def exc(self, command, *args):
        """ Wrapper for sqlite exec. """
        connection = sqlite3.connect(self.path)

        if self.verbose:
            print(command, args)

        try:
            cursor = connection.cursor()
            cursor.execute(command, *args)
        except sqlite3.Error:
            connection.rollback()
        else:
            connection.commit()

    def qry(self, query, *args):
        """ Wrapper for sqlite exec. """
        connection = sqlite3.connect(self.path)

        if self.verbose:
            print(query, args)

        return connection.execute(query, *args)

    def list_app_items(self, app):
        """ Return all items listed in the app. """
        query = """
        SELECT app, object, type
        FROM inner
        INDEXED BY ix_app
        WHERE app = ?
        """

        return self.qry(query, app)

    def add_item(self, app, item, item_type):
        """ Simple wrapper for inserting item. """
        self.exc(
            """ INSERT OR IGNORE INTO inner (app, object, type)
            VALUES (?, ?, ?) """,
            app, item, item_type
        )

    def add_app(self, app, source, target):
        """ Simple wrapper for inserting app. """
        self.exc(
            """ INSERT OR IGNORE INTO app (app, source_path, target_path)
            VALUES (?, ?, ?) """,
            app, source, target
        )


def install():
    """ Create basic db. """
    db = DB.get_instance()

    db.exc("""CREATE TABLE IF NOT EXISTS apps
    (
        app         TEXT NOT NULL UNIQUE,
        source_path TEXT NOT NULL UNIQUE,
        target_path TEXT NOT NULL UNIQUE
    )
    """)
    db.exc("""CREATE TABLE IF NOT EXISTS inner
    (
        app    TEXT NOT NULL UNIQUE,
        object TEXT NOT NULL UNIQUE,
        type   TEXT NOT NULL UNIQUE
    )
    """)

    db.exc("""CREATE INDEX ix_app ON inner (app) """)
