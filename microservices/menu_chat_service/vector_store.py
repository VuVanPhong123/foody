import os
import numpy as np
from typing import List, Dict, Tuple
from google import genai
from sklearn.metrics.pairwise import cosine_similarity
from google.genai.types import EmbedContentConfig
class MenuVectorStore:
    def __init__(self, api_key, model="models/embedding-001"):
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.vectors = []
        self.documents = []
        
    def load_menu_data(self, menu_file: str):
        """Load menu data and split into chunks"""
        if not os.path.exists(menu_file):
            raise FileNotFoundError(f"Menu file {menu_file} not found")
            
        with open(menu_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Split menu into individual items
        menu_items = []
        current_item = []
        
        for line in content.splitlines():
            if line.strip() == "":
                if current_item:
                    menu_items.append("\n".join(current_item))
                    current_item = []
            else:
                current_item.append(line)
                
        if current_item:  # Add the last item
            menu_items.append("\n".join(current_item))
            
        # Store as documents
        self.documents = menu_items
        
        # Create embeddings for each menu item
        self._create_embeddings()
        
        return len(self.documents)
        
    def _create_embeddings(self):
        """Create embeddings for all documents"""
        self.vectors = []
        
        for doc in self.documents:
            embedding = self._get_embedding(doc)
            self.vectors.append(embedding)
            
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text"""
        try:
            result = self.client.models.embed_content(
                model=self.model,
                contents=text,
                config=EmbedContentConfig()
            )
            # Extract the embedding values from the response
            return result.embeddings[0].values
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [0.0] * 768  # Default dimension for embedding-001
            
    def search(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """Search for most relevant menu items"""
        # Get query embedding
        query_embedding = self._get_embedding(query)
        
        # Calculate similarity with all documents
        similarities = []
        for vec in self.vectors:
            # Convert to numpy arrays for cosine similarity
            vec_np = np.array(vec).reshape(1, -1)
            query_np = np.array(query_embedding).reshape(1, -1)
            
            sim = cosine_similarity(vec_np, query_np)[0][0]
            similarities.append(sim)
            
        # Get top-k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append((self.documents[idx], similarities[idx]))
            
        return results 