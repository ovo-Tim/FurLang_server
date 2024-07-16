'''
    We use this file to warp the apis of NLP libraries(like spacy, lemminflect),
    so that we can support other languages or replace the back-end easily.
'''
import spacy
import lemminflect
import re

SPACY_MOUDLE = 'en_core_web_sm' # 12Mb

nlp = spacy.load(SPACY_MOUDLE)
def lemmatize(sentence:str, exclusion_list:list[str]=[]) -> list[tuple[str, str]]:
    res = []
    for i in nlp(sentence):
        if (not re.fullmatch(r'\b[A-Za-z][a-z]*\b', i.text)) or (i in exclusion_list) or (len(i)<3): # Filter non-words
            continue
        res.append((i.text, i._.lemma()))
    return res