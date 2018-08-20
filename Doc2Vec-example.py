#Import all the dependencies
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
from gensim.models.doc2vec import Doc2Vec

data = ["I love machine learning. Its awesome.",
        "I love coding in python",
        "I love building chatbots",
        "they chat amagingly well"]

docs = ["no common words", 2]

tagged_data = [TaggedDocument(data, tags=[str(i)]) for i, _d in enumerate(data)]

max_epochs = 100
vec_size = 20
alpha = 0.025

model = Doc2Vec(size=vec_size,
                alpha=alpha,
                min_alpha=0.00025,
                min_count=1,
                dm=1)

model.build_vocab(tagged_data)

for epoch in range(max_epochs):
    print('iteration {0}'.format(epoch))
    model.train(tagged_data,
                total_examples=model.corpus_count,
                epochs=model.iter)
    # decrease the learning rate
    model.alpha -= 0.0002
    # fix the learning rate, no decay
    model.min_alpha = model.alpha

model.save("d2v.model")
print("Model Saved")

model= Doc2Vec.load("d2v.model")
#to find the vector of a document which is not in training data
test_data = word_tokenize("baby".lower())
v1 = model.infer_vector(test_data)
print("Test Data Vectors ", v1)

# to find most similar doc using tags
similar_doc = model.docvecs.most_similar('1')
print("similarity distance between test and training data")
print(similar_doc)

tokens = "a new sentence to match".split()

new_vector = model.infer_vector(tokens)
sims = model.docvecs.most_similar([new_vector])
print("similar data - find out most similar data- amount of similarity")
print(sims)

# to find vector of doc in training data using tags or in other words, printing the vector of document at index 1 in training data
print("Vector of a doc in training data")
print(model.docvecs['1'])
