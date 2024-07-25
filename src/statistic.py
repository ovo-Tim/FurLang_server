import ujson
from datetime import datetime, timedelta
import atexit
from pathlib import Path

MAX_OPERATION_SIENCE_SKIP = 10

class statistic:
    def __init__(self, path:Path) -> None:
        self.path = path
        with open(path) as f:
            self.data: dict = ujson.load(f)
        self.clean_old()

        self._operation = 0
        atexit.register(self.save, force=True)

    def clean_old(self) -> None:
        for i in self.data.keys():
            d = datetime.strptime(i, "%Y-%m-%d")
            if d < (datetime.now() - timedelta(days=7)):
                del self.data[i]

    def save(self, force:bool = False) -> None:
        if not force and self._operation < MAX_OPERATION_SIENCE_SKIP:
            self._operation += 1
            return
        self._operation = 0
        with open(self.path, 'w') as f:
            ujson.dump(self.data, f)

    def get(self) -> dict:
        return self.data

    def __ins(self, fam: float):
        if fam > 0.85:
            self.data['learned'] += 1
        elif fam > 0.6:
            self.data['familiar'] += 1
        elif fam > 0.4:
            self.data['unfamiliar'] += 1
        else:
            self.data['new'] += 1

    def add(self, fam:float):
        d = datetime.now().strftime("%Y-%m-%d")
        if d not in self.data:
            self.data[d] = {
                'learned': 0,
                'familiar': 0,
                'unfamiliar': 0,
                'new': 0
            }
        self.__ins(fam)
        self.save()