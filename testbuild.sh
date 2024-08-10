python -m venv /tmp/testenv
source /tmp/testenv/bin/activate
pip install -r ./requirements.txt
pip install nuitka
python -m spacy download en_core_web_sm
nuitka --standalone --include-data-dir=Dicts=Dicts --include-data-dir=defaults=defaults --assume-yes-for-downloads --output-dir=build --spacy-language-model=en_core_web_sm --clang --script-name=main.py
