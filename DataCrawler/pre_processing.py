import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import string

class PreProcessing(object):
    def __init__(self):
        self._emoticons_str = r"""
            (?:
                [:=;] # Eyes
                [oO\-]? # Nose (optional)
                [D\)\]\(\]/\\OpP] # Mouth
            )"""

        self._regex_str = [
            self._emoticons_str,
            r'<[^>]+>',  # HTML tags
            r'(?:@[\w_]+)',  # @-mentions
            r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # hash-tags
            r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',  # URLs

            r'(?:(?:\d+,?)+(?:\.?\d+)?)',  # numbers
            r"(?:[a-z][a-z'\-_]+[a-z])",  # words with - and '
            r'(?:[\w_]+)',  # other words
            r'(?:\S)'  # anything else
        ]

        punctuation = list(string.punctuation)
        self._stops = stopwords.words('english') + punctuation + ['rt', 'via']

        self._tokens_re = re.compile(r'(' + '|'.join(self._regex_str) + ')', re.VERBOSE | re.IGNORECASE)
        self._emoticon_re = re.compile(r'^' + self._emoticons_str + '$', re.VERBOSE | re.IGNORECASE)


    def tokenize(self,s):
        s = s.replace("'", " ")
        return self._tokens_re.findall(s)

    def preprocess(self,s):

        prefix = ('@','http://','https://',':',"/")

        ps = PorterStemmer()
        tokens = self.tokenize(s)

        tokens = [token if self._emoticon_re.search(token) else token.lower() for token in tokens]
        terms_stop = [term for term in tokens  if term not in self._stops]
        #print(terms_stop)
        #terms_stop = [ps.stem(term) for term in terms_stop]

        PorterStemmer().stem('speaker')

        # if self._emoticon_re.search(t) is not None:
        for t in terms_stop[:]:
            #     terms_stop.remove(t)
            if t.startswith(prefix):
                terms_stop.remove(t)
            if not PreProcessing.isEnglish(t):
                terms_stop.remove(t)
            #print(self._emoticon_re.search(t))
            # if self._emoticon_re.search(t):
            #     terms_stop.remove(t)
        return terms_stop

    def isEnglish(words):
        try:

            words.encode('ascii')

        except UnicodeEncodeError:
            return False
        else:
            return True




