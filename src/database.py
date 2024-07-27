from typing import Any
import ujson as json
import time
import logging
from . import nlp
from datetime import datetime
from scipy.stats import norm
import sqlite3
import os
from types import FunctionType
import re
import copy
from src import statistic as sta

MAX_OPERATION_SIENCE_SKIP = 10 # SQL won't save datas untill request times exceed MAX_OPERATION_SIENCE_SKIP.

def calculateWordFamiliarity(frequency: int)->float:
    return round(float(norm.pdf(frequency, 6, 2.1)), 2)

def good_sentence(sentence:str|None)->bool:
    if sentence is None:
        return False
    con1 = len(sentence.split(' ', maxsplit=3))==4
    con2 = re.fullmatch(r'''^(?!.*[^a-zA-Z0-9\s.,!?;:()'"-]).*$''', sentence) is not None
    return con1 and con2

class _hook_dict:
    def __init__(self, word:str, set_word:FunctionType, data:dict) -> None:
        self.val = data
        self.__word = word
        self.__set_word = set_word

    def __getitem__(self, key) -> Any:
        if (key == 'sentences' or key == 'notes') and self.val[key] is None:
            return []
        return self.val[key]

    def __setitem__(self, key, value):
        self.__set_word(self.__word, key, value)
        self.val[key] = value

class words_db:
    def __init__(self, path) -> None:
        '''
            word TEXT PRIMARY KEY,
            frequency INTEGER,
            familiarity REAL,
            last_used_date TEXT,
            notes TEXT, // List to json
            sentences TEXT // List to json
        '''
        self._keys_cache_available = False
        self._keys_cache = []

        self._operation_count = 0

        if not os.path.exists(path):
            _init = True
        else:
            _init = False
        self._db = sqlite3.connect(path)
        # self.cursor.execute('BEGIN TRANSACTION')
        if _init:
            self.init_db()

    def init_db(self):
        self._db.execute("""
            CREATE TABLE words(
                word TEXT PRIMARY KEY NOT NULL,
                frequency INTEGER,
                familiarity REAL,
                sentences TEXT,
                last_used_date TEXT,
                notes TEXT
            )
        """)

    def __getitem__(self, word):
        res = self._db.execute(f"SELECT * FROM words WHERE word='{word}'").fetchone()
        val = {
            'frequency': res[1],
            'familiarity': res[2],
            'sentences': (json.loads(res[3]) if (res[3] is not None) else []),
            'last_used_date': res[4],
            'notes': json.loads(res[5])
        }
        return _hook_dict(word, self.set_word, val)

    def __setitem__(self, key, value:dict):
        fer = value['frequency']
        fam = value['familiarity']
        last_used_date = value['last_used_date']
        sentences = json.dumps(value['sentences'])
        notes = json.dumps(value['notes'])
        self._db.execute("INSERT OR REPLACE INTO words VALUES (?, ?, ?, ?, ?, ?)", (key, fer, fam, sentences, last_used_date, notes))
        self._keys_cache_available = False
        self.__save()

    def keys(self):
        if not self._keys_cache_available:
            self._keys_cache = [i[0] for i in self._db.execute("SELECT word FROM words").fetchall()]
            self._keys_cache_available = True

        return self._keys_cache

    def __del__(self):
        self._db.commit()
        self._db.close()

    def __save(self):
        self._operation_count += 1
        if self._operation_count > MAX_OPERATION_SIENCE_SKIP:
            self._db.commit()
            self._operation_count = 0

    def set_word(self, word:str, key:str, value):
        if key == 'sentences' or key == 'notes':
            value = json.dumps(value)
        self._db.execute(f"UPDATE words SET {key} = ? WHERE word = ?", (value, word))
        self.__save()

    def get_learned(self) -> int:
        return self._db.execute('SELECT COUNT(*) FROM words WHERE familiarity > 0.85').fetchone()[0]

    def __len__(self):
        return len(self.keys())

class datas():
    '''
        An interface for exchanging data.
        DO NOT read/write _db directly, it's possible we change the data storage mode.
    '''
    def __init__(self, db_path, excluded_words_path, statistic:sta.statistic) -> None:
        self._db_path = db_path
        self._excluded_words_path = excluded_words_path
        self._save_request_times = 0
        self.statistic = statistic

        s = time.time()
        with open(self._excluded_words_path,) as f:
            self.excluded_words = json.load(f)
        self._db = words_db(self._db_path)
        logging.debug(f"Database load time:{ time.time()-s }s")

    def add_ExcludedWords(self, words:list):
        self.excluded_words += words

    def add_NewWord(self, word:str, sentence:list[str]|None=[], lemmatize=False):
        '''
            To avoid adding repetitive words, please make sure your word has been lemmatized or set the lemmatize parameter to True.
            We highly suggest you lemmatize words with sentences, instead lemmatize here.
        '''
        if lemmatize:
            word=nlp.lemmatize(word)[0][1]
        if word in self._db.keys():
            logging.warn("Word has already exist. Skipped.")
        self._db[word] = {
            'frequency': 1,
            'familiarity': 0.01,
            'sentences': sentence,
            'last_used_date': str(datetime.now().date()),
            'notes': []
        }

    def get_word(self, word:str, sentence:str|None=None,auto_create=True, update=True , lemmatize=False)->dict|None:
        '''
            Return None if word is in excluded_words.
        '''

        word = word.lower()
        if lemmatize:
            word = nlp.lemmatize(word)[0][1]

        if word in self.excluded_words:
            logging.debug(f"Word { word } is in excluded_words. Skipped.")
            return None

        if not good_sentence(sentence):
            sentence = None

        if word not in self._db.keys():
            if auto_create:
                self.add_NewWord(word, sentence=[sentence] if sentence is not None else [])
                return self._ret_info(self._db[word].val, word)
            else:
                logging.error(f"datas.get_word: Can't find word '{ word }', and auto_create is disabled.")
                return None

        # Update word info
        if update:
            self._word_update(word, sentence)

        self.statistic.add(self._db[word]['familiarity'])
        return self._ret_info(self._db[word].val, word)

    def _ret_info(self, res:dict, word:str):
        res = copy.copy(res)
        res['word'] = word
        return res

    def _word_update(self, word:str, sentence:str|None=None):
        self._db[word]['frequency'] += 1
        self._db[word]['familiarity'] += calculateWordFamiliarity(self._db[word]['frequency'])
        self._db[word]['last_used_date'] = str(datetime.now().date())
        if (sentence is not None) and (sentence not in self._db[word]['sentences']):
            updated = self._db[word]['sentences']
            updated.append(sentence)
            self._db[word]['sentences'] = updated

    def update_sentences(self, word:str, new: list[str]):
        self.set_word(word, "sentences", new)

    def update_notes(self, word:str, new: list[str]):
        self.set_word(word, "notes", new)

    def set_word(self, word:str, key:str, value):
        self._db.set_word(word, key, value)

    def __getitem__(self, key):
        '''
            Get word info without updating; Get excluded words.
            key: 'excluded_words' or the word you want to seek.
        '''
        if key == 'excluded_words':
            return self.excluded_words
        else:
            return self._db[key]

    def __setitem__(self, key:tuple[str, Any], value):
        '''
            Set words attributes, use datas[(word, attribute)]=sth.
        '''

        self._db['word'][key[0]][key[1]] = value

    def __len__(self):
        return len(self._db)

    def get_learned(self) -> int:
        return self._db.get_learned()