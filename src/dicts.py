import os
from pathlib import Path
import logging, time
import sqlite3
import ujson as json

class dicts:
    def __init__(self, dicts_path) -> None:
        self._dicts_path = Path(dicts_path)
        self._dbs = []
        self.load()

    def load(self):
        logging.info(f"Loading dictionaries... From {self._dicts_path}")
        for f in self._dicts_path.glob("*.db"):
            try:
                self._dbs.append(sqlite3.connect(f))
            except Exception as e:
                logging.error(f"Failed to load {f}: {e}. Skipping.")

    def query(self, query:str) -> list[str]:
        '''
            Search in all dictionaries, return a list of html.
        '''
        return [d.execute("SELECT * FROM words WHERE word = ?", (query))[2] for d in self._dbs]



