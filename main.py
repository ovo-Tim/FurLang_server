from src import server
from src import database
from src import dicts
from src import statistic
import ujson
import logging
from os.path import dirname
from pathlib import Path
import shutil
from typing import Any
logging.basicConfig(level=logging.INFO)

class _conf:
    def __init__(self, conf_dir:Path) -> None:
        with open(conf_dir/'config.json') as f:
            self.conf = ujson.load(f)

    def __getitem__(self, key) -> Any:
        if 'path' in key:
            val:str = self.conf[key]
            return Path(val).expanduser()
        return self.conf[key]

conf_dir = Path('~/.furlang').expanduser()
if not conf_dir.exists():
    logging.info(f"Create config directory at {conf_dir}")
    # conf_dir.mkdir(parents=True)
    shutil.copytree(f'{dirname(__file__)}/defaults', conf_dir)

conf = _conf(conf_dir)
sta = statistic.statistic(conf['statistic_path'])
datas = database.datas(conf['db_path'], conf['excluded_words_path'], sta)
dictionary = dicts.dicts(conf['dicts_path'])
ser = server.init(datas, dictionary, port=conf['port'])
ser.serve_forever()