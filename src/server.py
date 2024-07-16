import logging
from .nlp import lemmatize
import ujson as json
from .database import datas
from flask import Flask, request
from flask_restful import Resource, Api
from gevent import pywsgi
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)

class service(Resource):
    def __init__(self, database) -> None:
        super().__init__()
        self.database: datas = database

    def post(self):
        logging.debug(f"Received message.")
        t = request.get_json()
        rep = self.msg_process(t['type'], t['data'])
        logging.debug(f"Reply: {rep}")
        return rep

    def msg_process(self, type:str, data):
        match type:
            case 'get':
                words = lemmatize(data)
                return self.get_marking_words(words, sentence=data)
            case 'test':
                return 'FurLang!'
            case _:
                return None

    def get_marking_words(self, words:list[tuple[str, str]], sentence:str|None=None) -> list:
        res = []
        for (origin, lemmatized) in words:
            info = self.database.get_word(lemmatized, sentence=sentence)
            if info is None or info['familiarity'] > 0.85:
                continue
            res.append((origin, info))
        return res

def init(database, port:int=1028):
    api.add_resource(service, '/', resource_class_args=[database])
    logging.info(f"Start service on {port}")
    return pywsgi.WSGIServer(('127.0.0.1', port), app)