import logging
from .nlp import lemmatize
from .database import datas
from flask import Flask, request
from flask_restful import Resource, Api
from gevent import pywsgi
from flask_cors import CORS
from src.dicts import dicts


app = Flask(__name__)
api = Api(app)
CORS(app)

class service(Resource):
    def __init__(self, database, dictionary) -> None:
        super().__init__()
        self.database: datas = database
        self.dictionary: dicts = dictionary

    def post(self):
        t = request.get_json()
        logging.debug(f"Received message: {t}")
        rep = self.msg_process(t['type'], t['data'])
        logging.debug(f"Reply: {rep}")
        return rep

    def msg_process(self, type:str, data):
        match type:
            case 'get':
                words = lemmatize(data)
                return self.get_marking_words(words, sentence=data)
            case 'query_dicts':
                return self.dictionary.query(data)
            case 'update_sentences':
                self.database.update_sentences(data[0], data[1])
                return True
            case 'update_notes':
                logging.debug(f"Updating {data}")
                self.database.update_notes(data[0], data[1])
                return True
            case 'get_info':
                return self.database.get_word(data, update=False)
            case 'get_statistic':
                return self.database.statistic.get()
            case 'learned_count':
                return (self.database.get_learned(), len(self.database))
            case 'test':
                return 'FurLang!'
            case _:
                return None

    def get_marking_words(self, words:list[tuple[str, str]], sentence:str|None=None) -> list:
        res = []
        tmp = []
        words = [word for word in words if word[0] not in tmp and not tmp.append(word[0])]
        for (origin, lemmatized) in words:
            info = self.database.get_word(lemmatized, sentence=sentence)
            if info is None or info['familiarity'] > 0.85:
                continue
            res.append((origin, info))
        return res

def init(database, dictionary, port:int=1028):
    api.add_resource(service, '/', resource_class_args=[database, dictionary])
    logging.info(f"Start service on {port}")
    return pywsgi.WSGIServer(('127.0.0.1', port), app)