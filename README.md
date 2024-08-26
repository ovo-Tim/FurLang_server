# Furry Language Server
This is the server for [Furry Language](https://github.com/ovo-Tim/FurLang_app). In normal case, you don't need to install it, instead you should install [FurLang App](https://github.com/ovo-Tim/FurLang_app) which has included the server.

## Contributing
The code quality is just ok, and the API design is bad. Feel free to open an issue or pull request.

### Installation
Just run commands below:
``` bash
pip install -r ./requirements.txt
python -m spacy download en_core_web_sm
```
If you needs dicts, run this command to download the default dict:
``` bash
curl -Ljo ./Dicts/dict.db https://github.com/ovo-Tim/mdict2sql/releases/download/example/dict.db
```
Or read [this](./Dicts/readme.md) to make dicts yourself.