# I don't actually think tests for this simple project are necessary.

from pathlib import Path
import unittest
import sys
import shutil
sys.path.append('./')

try:
    shutil.rmtree(Path('~/.furlang').expanduser())
except:  # noqa: E722
    pass

class TestFileMethods(unittest.TestCase):

    def setUp(self):
        global main, nlp
        import main
        from src import nlp

    def test_nlp(self):
        self.assertEqual(nlp.lemmatize('Furry is the best'), [('Furry', 'furry'), ('the', 'the'), ('best', 'good')])

    def test_dictionary(self):
        self.assertIsNot(main.dictionary.query('furry')[0], "")
        self.assertIsNotNone(main.dictionary.query('word'))

    def test_database(self):
        self.assertIsNotNone(main.datas.get_word('furry'))
        self.assertEqual(main.datas.get_learned(), 0)
        main.datas.update_notes('furry', ['test'])
        main.datas.update_sentences('furry', ['test'])
        self.assertIsNotNone(main.datas.statistic.get())

if __name__ == '__main__':
    unittest.main()
