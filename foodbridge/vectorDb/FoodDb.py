import threading
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions
import chromadb.utils.embedding_functions as embedding_functions

PAIR_CSV = "food_pair.csv"

class FoodDb:
    _instance = None
    _lock = threading.Lock()
    _sentenceTransformer = SentenceTransformer("all-MiniLM-L6-v2")
    _client = chromadb.PersistentClient(path="food_db")
    _collection = _client.get_or_create_collection(
        name="foods",
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        ),

    )

    def add(self, ids, documents):
        self._collection.add(
            ids=ids,  # Use food names as unique IDs
            documents=documents,  # Store descriptions as retrievable data
        )
    
    def search_similar_foods(self, query: str, n_results: int = 10):
        df = pd.read_csv(PAIR_CSV)
        item_doc = {}
        results = self._collection.query(
            query_texts=[query],
            n_results=n_results,
        )
        for i in range(len(results["ids"][0])):
            if results["documents"] != None:
                item_doc[results["ids"][0][i]] = df[df["food_name"] == results["ids"][0][i]]["nutrition_info"].iloc[0]
        return item_doc

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

def Test():
    # Create Chroma client and collection
    client = chromadb.PersistentClient(path="food_db")
    collection = client.get_or_create_collection(
        name="foods",
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        ),
    )
    
    # # Sample data: Keys = food names, Values = descriptions
    # documents = {
    #     "apple pie": "A delicious dessert made with apples and cinnamon.",
    #     "chicken curry": "Spicy curry with chicken and various spices.",
    #     "beef stew": "Hearty stew with beef, carrots, and potatoes.",
    #     "fruit pastry": "Flaky pastry filled with mixed fruits.",
    #     "pasta, beef with siders and stuff": "Italian dish made with pasta and tomato sauce.",
    #     "Whiskey":"Whiskey is a type of distilled alcoholic beverage made from fermented grain mash."
    # }
    
    # Add documents to Chroma
    # food_names = list(documents.keys())
    # descriptions = list(documents.values())
    food_names = []
    descriptions = []

    food_data = pd.read_csv(PAIR_CSV)
    food_set = set()
    for index, row in food_data.iterrows():
        food_name = row["food_name"]
        print(food_name)
        content = row["nutrition_info"]
        if type(content) == str and len(food_name) > 0 and len(content) > 0 and food_name not in food_set:
            food_names.append(food_name)
            descriptions.append(content)
            food_set.add(food_name)

    print(f"Adding {len(food_names)} items to the database")
    
    collection.add(
        ids=food_names,  # Use food names as unique IDs
        documents=food_names,  # Store descriptions as retrievable data
    )
    
    # Query by similarity to food names
    def search_similar_foods(query: str, n_results: int = 2):
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
        )
        return results
    
    # Example usage
    query = "Almond Chicken"
    results = search_similar_foods(query, n_results=4)  # Increase n_results
    
    print("Query:", query)
    for food_name, desc in zip(results["ids"][0], results["documents"][0]):
        print(f"\nFood: {food_name}")
        print(f"Description: {desc}")

if __name__ == "__main__":
    Test()