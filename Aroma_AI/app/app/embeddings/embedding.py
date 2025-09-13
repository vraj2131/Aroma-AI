from langchain_community.embeddings import HuggingFaceEmbeddings

class HuggingFaceEmbedder:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2", cache_folder="./sentence-transformers-cache"):
        self.model_name = model_name
        self.cache_folder = cache_folder
        self.embedding_model = None
        
    def initialize_embeddings(self):
        if not self.embedding_model:
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=self.model_name,
                cache_folder=self.cache_folder
            )
        return self.embedding_model

# Usage:
embedder = HuggingFaceEmbedder()
huggingface_embeddings = embedder.initialize_embeddings()
