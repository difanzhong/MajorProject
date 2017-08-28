import MapShow.db
from collections import Counter
import json
from nltk.stem import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
import math

class Process(object):

    def __init__(self):
        self._counter = Counter()
        self._pse = SnowballStemmer('english')
        self._doc_collect = []
        self._idf_dict = {}
        self._terms = []

    def collect_words(self, suburb_id, date, hour):

        ds = MapShow.db.DBConnect()
        ds.connect()
        terms = ds.getTerms(suburb_id, date, hour)

        ps = PorterStemmer()

        if terms is not None:
            result = self.refine_terms(terms)
            print(result)
            ds.close()
            return result
        else:
            ds.close()
            return None

    def collect_allwords(self, date, hour):
        # collect words from db, return a dict with all terms and all documents

        ds = MapShow.db.DBConnect()
        ds.connect()
        terms = ds.getAllTerms(date, hour)

        if terms['document'] is not None:

            for doc in terms['document']:
                doc['terms'] = doc['terms'].replace("'", '')
                doc['terms'] = doc['terms'].replace("#", '')
                doc['terms'] = [self._pse.stem(term.strip()) for term in doc['terms'].split(',') if len(term) > 1]
                self._doc_collect.append(doc)

            print(len(terms['document']))

        if terms['words'] is not None:

            result = self.refine_terms(terms['words'])

            for term in result:

                self._terms.append(term)

            ds.close()

    def checkResult(self):
        print(self._doc_collect)
        print(self._terms)


    def tf_idf_table(self):

        try:
            tfidf_map = []
            idf_table = {}

            all_terms = self._terms
            documents = self._doc_collect

            for term in all_terms:

                tfidf_for_terms = {}
                no_of_doc_contain = 0

                for doc in documents:

                    text_arr = doc['terms']

                    occur = self.find_occurance(text_arr, term)

                    if occur > 0:
                        no_of_doc_contain += 1

                    tf = occur

                    doc_id = doc['suburb_id']

                    tfidf_for_terms[doc_id] = tf

                total_num_doc = len(documents)

                v = float(total_num_doc) / float(no_of_doc_contain)
                idf = math.log(v, 2)

                idf_table[term] = idf

                # for i in range(len(tfidf_for_terms)):
                #     tf = tfidf_for_terms[i]
                #     tfidf_for_terms[i] = tf * idf

                for key,value in tfidf_for_terms.items():

                    tfidf_for_terms[key] = int(value) * idf

                tfidf_map.append(tfidf_for_terms)

            self._idf_dict = idf_table

            tfidf_documents = {}

            for doc in documents:
                tfidf_for_doc = []

                document_id = doc['suburb_id']

                for term in tfidf_map:
                    tfidf_for_doc.append(term[document_id])

                tfidf_documents[document_id]=tfidf_for_doc

            return tfidf_documents
        except:
            return None



    def find_occurance(self, text, term):
        num = 0
        for word in text:
            if term == word:
                num += 1
        return num

    def GenerateQueryDoc(self, query):

        tfidfs = []

        query = [self._pse.stem(q) for q in query]

        if len(self._terms) > 0:
            Terms = self._terms
            for term in Terms:

                occur = self.find_occurance(query, term)

                tf = float(occur)

                if len(self._idf_dict) > 0:
                    idf = self._idf_dict[term]

                    tfidf = tf * idf
                    tfidfs.append(tfidf)

        return tfidfs

    def RankCosineSimilarities(self, Query, Documents):

        cosineSimilarities = {}

        for docName, tdidf in Documents.items():
            cosineSimilarity = self.CalculateCosineSimilarity(Query, tdidf)
            cosineSimilarities[docName] = cosineSimilarity

        return sorted(cosineSimilarities.items(), key=lambda item: (item[1], item[0]), reverse=True)

    def CalculateCosineSimilarity(self, Query, Document):
        upper = 0
        lowerLeft = 0
        lowerRight = 0

        for index in range(len(Document)):
            upper += (Query[index] * Document[index])
            lowerLeft += math.pow(Query[index], 2)
            lowerRight += math.pow(Document[index], 2)

        cosineSimilarity = 0

        if (lowerLeft * lowerRight) != 0:
            cosineSimilarity = upper / math.sqrt(lowerLeft * lowerRight)

        return cosineSimilarity


    def refine_terms(self,terms):

        if terms is not None:
            terms = terms.replace("'",'')
            terms = terms.replace("#", '')
            termsList = [self._pse.stem(term.strip()) for term in terms.split(',') if len(term) > 1]
            termsList = [term for term in termsList if len(term) > 1 ]
            result = dict(Counter(termsList).most_common(1500))

            return result

    def term_frequency(self, terms):

        self._word_count.update(terms)

        print(terms)


class document(object):

    def __init__(self, suburb_id, hour, termCollection):
        self._sub_id = suburb_id
        self._hour = hour
        self._term_collect = termCollection
        self._terms_count = None

class documentCollection(object):

    def __init__(self):
        self._doc_list = []