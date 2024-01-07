from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from scipy.sparse import csr_matrix
import random

app = Flask(__name__)

## implementatiion of the lda on github.com/vvennela/ml/lda. API tested with postman. 

@app.route('/api', methods=['POST'])
def process_document():
   data = request.json
   document = data['document']
   num_topics = data['num_topics']

   text_file = open("corpus.txt", "r")
   data_samples = text_file.readlines()
   random.shuffle(data_samples)

# Split the data into training and testing sets
   split_percentage = 90
   X_train_document, X_test_document = np.split(data_samples, [int(len(data_samples)*(split_percentage/100))])
   tfidf_vectorizer = TfidfVectorizer(max_df = 0.95, min_df = 100, stop_words = 'english')
   tfidf = tfidf_vectorizer.fit_transform(data_samples) 
   tfidf = tfidf.toarray()
   l, _ = tfidf.shape
   X_train, X_test = np.split(tfidf, [int(l*(split_percentage/100))])
   X_train = csr_matrix(X_train)
   X_test = csr_matrix(X_test)

# Fit LDA model
   topics = num_topics
   model = LatentDirichletAllocation(n_components = topics)
   model.fit(X_train)


   tf_feature_names = tfidf_vectorizer.get_feature_names_out()
   top_words = {}
   for topic_idx, topic in enumerate(model.components_):
      top_words[topic_idx] = [tf_feature_names[i] for i in topic.argsort()[:-10 - 1:-1]]

   # Get the topic for the document
   tf_feature_names = tfidf_vectorizer.get_feature_names_out()
   tfidf = tfidf_vectorizer.transform([document])
   tfidf = tfidf.toarray()
   l, _ = tfidf.shape
   X_train = csr_matrix(tfidf)
   p = model.transform(X_train)
   t = p.argmax()

   # Get the top words for the topic
   top_words = []
   for topic_idx, topic in enumerate(model.components_):
       if topic_idx == t:
           top_words = [tf_feature_names[i] for i in topic.argsort()[:-10 - 1:-1]]

   # Return the results
   return jsonify({
       'topic': t,
       'top_words': top_words
   })

if __name__ == '__main__':
   app.run(debug=True)
