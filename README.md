# CENG596 Information Retrieval System

This repository contains an Information Retrieval (IR) system using the Cranfield dataset, complete with a user interface developed in React.

## Repository Structure

The repository is divided into two main folders:

1. **ir_system** - Contains a Colab notebook which can be run directly. The notebook performs the following operations:
   - Evaluates the initial rankings of the Cranfield dataset using traditional methods such as PyTerrier indexing and BM25.
   - Generates embeddings for documents and queries in the dataset to evaluate performance.
   - Retrieves the top 10 documents using a FAISS index.
   - Reranks these 10 documents using a cross-encoder with the initial query to get the top 5.
   - Saves the document embeddings for later use with the interface.

2. **app** - Houses the React application which serves as the user interface.
   - Includes a `requirements.txt` file for setting up the necessary Python environment.
   - `query.py` acts as the backend, implementing Rocchio-based relevance feedback.

## Installation and Usage

To run this project, follow these steps:

1. **Backend Setup:**
   - Install Python dependencies: `pip install -r requirements.txt`
   - Execute the backend script: `python query.py`

2. **Frontend Setup:**
   - Install JavaScript dependencies: `yarn install`
   - Start the React application: `yarn start`

Once the interface is running on the server, users can interact with the system as follows:
   - Enter a query and select the number of documents to be retrieved.
   - Choose sorting by length or relevance.
   - View the retrieved documents and mark them as relevant or not.
   - Observe the reranked results based on the feedback provided.

## Authors

- Derya Tınmaz - deryatnmaz@gmail.com
- Mehmet Erdeniz Aydoğdu - erd.aydogdu05@gmail.com
