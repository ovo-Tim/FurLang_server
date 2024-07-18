from src import server
from src import database
from src import dicts
import ujson
import logging
from os.path import dirname
logging.basicConfig(level=logging.INFO)

with open(f'{dirname(__file__)}/config.json') as f:
    conf = ujson.load(f)
datas = database.datas(conf['db_path'], conf['excluded_words_path'])
dictionary = dicts.dicts(conf['dicts_path'])
ser = server.init(datas, port=conf['port'])
ser.serve_forever()