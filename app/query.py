from flask import Flask, request, render_template_string, make_response, jsonify
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
import ir_datasets
from annoy import AnnoyIndex
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/": {"origins": "http://localhost:3000"}, r"/feedback": {"origins": "http://localhost:3000"}})
app.config['CORS_HEADERS'] = 'Content-Type'

# Load the dataset
cranfield = ir_datasets.load("cranfield")

# Load pre-trained model and embeddings
model = SentenceTransformer("all-mpnet-base-v2")
d_e = np.load('./document_embeddings.npy')  # Load document embeddings
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')



# Create Annoy index
index = AnnoyIndex(d_e.shape[1], 'euclidean')
for i, vector in enumerate(d_e):
    index.add_item(i, vector)
index.build(10)

def build_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def retrieve_documents(query, k=5, sort_by='relevance', ascending=False):
    query_embedding = model.encode(query)
    max_attempts = 10  # Max number of attempts to retrieve enough documents
    multiplier = 2  # Multiplier to increase the number of documents to retrieve each iteration
    
    # Initial number of documents to retrieve
    retrieve_count = k*2
    
    for _ in range(max_attempts):
        # Retrieve documents using the Annoy index
        I, D = index.get_nns_by_vector(query_embedding, retrieve_count, include_distances=True)
        
        # Lookup documents by index and filter out empty texts
        doc_lookup = list(cranfield.docs_iter())
        retrieved_docs = [(doc_lookup[idx].doc_id, doc_lookup[idx].text, D[i]) for i, idx in enumerate(I) if len(doc_lookup[idx].text) > 0]
        
        # If we have enough documents, stop retrieving more
        if len(retrieved_docs) >= k*2:
            break
        
        # Increase the number of documents to retrieve in the next iteration
        retrieve_count *= multiplier
    
    # After retrieving and filtering, sort and trim the documents as needed
    if sort_by == 'relevance':
        retrieved_docs.sort(key=lambda x: x[2], reverse=not ascending)
    elif sort_by == 'length':
        retrieved_docs.sort(key=lambda x: len(x[1]), reverse=not ascending)
    
    # Trim the results to return exactly k documents, if possible
    documents = [(doc_id, doc_text) for doc_id, doc_text, score in retrieved_docs[:k*2]]
    pairs = [[query, doc[1]] for doc in documents]
    scores = cross_encoder.predict(pairs)
    reranked_docs = sorted(zip(scores, documents), reverse=True, key=lambda x: x[0])
    top_5_docs = [doc for _, doc in reranked_docs[:k]]

    return top_5_docs


def relevance_feedback(query,  relevant, irrelevant, k=5, sort_by='relevance', ascending=False):
    alpha = 1  # Weight for original query
    beta = 0.75  # Weight for relevant documents
    gamma = 0.25 
    relevant = [int(i) for i in relevant]
    irrelevant = [int(i) for i in irrelevant]
    relevant_vectors = d_e[relevant]
    irrelevant_vectors = d_e[irrelevant]
    query_embedding = model.encode(query)

    query_embedding = alpha * query_embedding + beta * np.mean(relevant_vectors, axis=0) - gamma * np.mean(irrelevant_vectors, axis=0)
    max_attempts = 10  # Max number of attempts to retrieve enough documents
    multiplier = 2  # Multiplier to increase the number of documents to retrieve each iteration
    
    # Initial number of documents to retrieve
    retrieve_count = k*2
    
    for _ in range(max_attempts):
        # Retrieve documents using the Annoy index
        I, D = index.get_nns_by_vector(query_embedding, retrieve_count, include_distances=True)
        
        # Lookup documents by index and filter out empty texts
        doc_lookup = list(cranfield.docs_iter())
        retrieved_docs = [(doc_lookup[idx].doc_id, doc_lookup[idx].text, D[i]) for i, idx in enumerate(I) if len(doc_lookup[idx].text) > 0]
        
        # If we have enough documents, stop retrieving more
        if len(retrieved_docs) >= k*2:
            break
        
        # Increase the number of documents to retrieve in the next iteration
        retrieve_count *= multiplier
    
    # After retrieving and filtering, sort and trim the documents as needed
    if sort_by == 'relevance':
        retrieved_docs.sort(key=lambda x: x[2], reverse=not ascending)
    elif sort_by == 'length':
        retrieved_docs.sort(key=lambda x: len(x[1]), reverse=not ascending)
    
    # Trim the results to return exactly k documents, if possible
    documents = [(doc_id, doc_text) for doc_id, doc_text, score in retrieved_docs[:k*2]]
    pairs = [[query, doc[1]] for doc in documents]
    scores = cross_encoder.predict(pairs)
    reranked_docs = sorted(zip(scores, documents), reverse=True, key=lambda x: x[0])
    top_5_docs = [doc for _, doc in reranked_docs[:k]]
    return top_5_docs

@app.route('/', methods=['GET', 'POST', 'OPTIONS'])
def search():
    if request.method == 'OPTIONS': 
        print("here")
        return build_preflight_response()
    documents = []
    query = ""
    if request.method == 'POST':
        query = request.json['query']
        num_docs = int(request.json.get('num_docs', 5))
        sort_by = request.json.get('sort_by', 'relevance')  # Default to sorting by relevance
        documents = retrieve_documents(query, k=num_docs, sort_by=sort_by, ascending=True)
    #return render_template_string(HTML, documents=documents, query=query)
    response = make_response(jsonify(documents))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.content_type = "application/json"
    return response

@app.route('/feedback/', methods=['POST', 'OPTIONS'])
def feedback():
    if request.method == 'OPTIONS': 
        print("here")
        return build_preflight_response()
    query = request.json['query']
    relevant = request.json['relevant']
    irrelevant = request.json['irrelevant']
    num_docs = int(request.json.get('num_docs', 5))
    sort_by = request.json.get('sort_by', 'relevance')  # Default to sorting by relevance

    documents = relevance_feedback(query,  relevant, irrelevant, num_docs,sort_by, ascending=True)
    response = make_response(jsonify(documents))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.content_type = "application/json"
    return response
    

if __name__ == "__main__":
    app.run(debug=True)
