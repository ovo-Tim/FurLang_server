'''
    We use this file to warp the apis of NLP libraries(like spacy, lemminflect),
    so that we can support other languages or replace the back-end easily.
'''
from spacy import load as spacy_load
import lemminflect  # noqa: F401
import re

SPACY_MOUDLE = 'en_core_web_sm' # 12Mb

nlp = spacy_load(SPACY_MOUDLE)
def lemmatize(sentence:str, exclusion_list:list[str]=[]) -> list[tuple[str, str]]:
    res = []
    for i in nlp(sentence):
        lemmaed = i._.lemma().lower()
        if (not re.fullmatch(r'\b[A-Za-z][a-z]*\b', lemmaed)) or (lemmaed in exclusion_list) or (len(lemmaed)<3): # Filter non-words
            continue
        res.append((i.text, lemmaed))
    return res