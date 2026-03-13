from sentence_transformers.SentenceTransformer import SentenceTransformer
from sentence_transformers.util.retrieval import semantic_search
import pickle

def initialize_recommender():
    """
    Creates the model and vector encodings for all resources and then saves them to a file for future loading.
    """

    model = SentenceTransformer('all-MiniLM-L6-v2')
    websites = [
    "How to Deal with Stress in College",
    "Healthy Organic Recipes and Cooking"
    ]

    website_embeddings = model.encode(websites)
    embeddings_data = {'Websites': websites, 'Embeddings': website_embeddings}
    with open('src/resources/website embeddings.pkl', 'wb') as f:
        pickle.dump(embeddings_data, f)
    model.save('src/resources/recommender_model')

def load_embeddings():
    """
    Loads vector embeddings for websites from pickle file
    """

    with open('src/resources/website embeddings.pkl', 'rb') as f:
        loaded_data = pickle.load(f)
    return loaded_data

def recommend(query):
    """
    Takes input from a user and performs a semantic search to do contextual matching with resources in the app

    Args:
        query: The message(s) that the recommendation will be based on

    Returns:
        recommendation: The name of the website that most closely matches the query
    """
    model = SentenceTransformer('src/resources/recommender_model')
    website_data = load_embeddings()
    websites = website_data['Websites']
    website_embeddings = website_data['Embeddings']
    query_encoding = model.encode(query)

    hits = semantic_search(query_encoding, website_embeddings, 2)
    return websites[hits[0][0]['corpus_id']]

def main():
    """
    Finds the recommended websites based on several queries and displays them
    """
    queries = ["Struggling with work and school",
               "Looking for new things to cook",
               "I am failing a class and need help",
               "I want to eat better"]
    
    for query in queries:
        recommendation = recommend(query)
        print("{} was the suggested website for your query of {}".format(recommendation,query))


if __name__ == '__main__':
    main()
    