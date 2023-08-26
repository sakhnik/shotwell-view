import common
import sqlite3


class Events:
    def __init__(self):
        self.events: {int: str} = {}  # eid -> path
        try:
            self.restore()
        except sqlite3.OperationalError:
            ...

    def get_name(self, id: int) -> str:
        return self.events.get(id)

    def set_name(self, id: int, name: str):
        self.events[id] = name

    def _get_db(self):
        return f'{common.ROOT}/events.db'

    def store(self):
        # Dump assigned event names to a database
        with sqlite3.connect(self._get_db()) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                )
            ''')

            for id, name in self.events.items():
                cursor.execute('INSERT INTO events (id, name) VALUES (?, ?)',
                               (id, name))
            conn.commit()

    def restore(self):
        self.events = {}
        # Connect to the SQLite database
        with sqlite3.connect(self._get_db()) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name FROM events')
            events = cursor.fetchall()
            for id, name in events:
                self.events[id] = name
