import gensim
from os import listdir
from nltk.tokenize import sent_tokenize
from gensim.models import doc2vec
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import gensim
from gensim.models.doc2vec import TaggedDocument
from collections import namedtuple
from smart_open import smart_open
from gensim.models import Doc2Vec
import gensim.models.doc2vec
from collections import OrderedDict
import multiprocessing
import numpy as np


#Get all the ceph data from get API request from SWAGGER API
docs = [f for f in listdir('/home/sunagara/PycharmProjects/Build_Logs_Aggregation/Build-Logs-Aggregation/logs/') if f.endswith('.txt')]
sent_tokenize_list = []
for doc in docs:
    with open('/home/sunagara/PycharmProjects/Build_Logs_Aggregation/Build-Logs-Aggregation/logs/'+doc)as data1:
        sent_tokenize_list.append(sent_tokenize(data1.read()))
print(sent_tokenize_list)
#Pass a tokenized version of the log file to the model

SentimentDocument = namedtuple('SentimentDocument', 'words tags split sentiment')

alldocs = []
with smart_open('/home/sunagara/PycharmProjects/Build_Logs_Aggregation/Build-Logs-Aggregation/logs/log1.txt', 'rb', encoding='utf-8') as alldata:
    for line_no, line in enumerate(alldata):
        tokens = gensim.utils.to_unicode(line).split()
        words = tokens[1:]
        #split the data into training and testing
        tags = [line_no] # 'tags = [tokens[0]]' would also work at extra memory cost
        split = ['train', 'test', 'extra', 'extra'][line_no//25000]  # 25k train, 25k test, 25k extra
        sentiment = [1.0, 0.0, 1.0, 0.0, None, None, None, None][line_no//12500] # [12.5K pos, 12.5K neg]*2 then unknown
        alldocs.append(SentimentDocument(words, tags, split, sentiment))

#Train all the docs and label them
train_docs = [doc for doc in alldocs if doc.split == 'train']
test_docs = [doc for doc in alldocs if doc.split == 'test']

print('%d docs: %d train-sentiment, %d test-sentiment' % (len(alldocs), len(train_docs), len(test_docs)))

#Reducing CPU time by assigning these parameters to model training
cores = multiprocessing.cpu_count()
assert gensim.models.doc2vec.FAST_VERSION > -1, "This will be painfully slow otherwise"

#Hyper tuning the models with different parameters and sending the train and test data to them for identifying if all combinations work to give accurate results
simple_models = [
    # PV-DBOW plain
    Doc2Vec(dm=0, vector_size=100, negative=5, hs=0, min_count=2, sample=0,
            epochs=20, workers=cores),
    # PV-DM w/ default averaging; a higher starting alpha may improve CBOW/PV-DM modes
    Doc2Vec(dm=1, vector_size=100, window=10, negative=5, hs=0, min_count=2, sample=0,
            epochs=20, workers=cores, alpha=0.05, comment='alpha=0.05'),
    # PV-DM w/ concatenation - big, slow, experimental mode
    # window=5 (both sides) approximates paper's apparent 10-word total window size
    Doc2Vec(dm=1, dm_concat=1, vector_size=100, window=5, negative=5, hs=0, min_count=2, sample=0,
            epochs=20, workers=cores),
]

#supply data to all the above models
for model in simple_models:
    model.build_vocab(alldocs)
    print("%s vocabulary scanned & state initialized" % model)

models_by_name = OrderedDict((str(model), model) for model in simple_models)

doc_id = np.random.randint(simple_models[0].docvecs.count)  # Pick random doc; re-run cell for more examples
print('for doc %d...' % doc_id)
for model in simple_models:
    inferred_docvec = model.infer_vector(alldocs[doc_id].words)
    print('%s:\n %s' % (model, model.docvecs.most_similar([inferred_docvec], topn=5)))

#inferred doc2vec does more calculation on cosine similarity with distance and list top 5 anomalous data
