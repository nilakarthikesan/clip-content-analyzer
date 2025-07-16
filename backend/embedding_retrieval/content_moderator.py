import numpy as np
import torch
from typing import List, Dict, Tuple
from transformers.models.clip.processing_clip import CLIPProcessor
from transformers.models.clip.modeling_clip import CLIPModel
from PIL import Image
import json

class ContentModerator:
    def __init__(self, clip_model, clip_processor):
        """
        Initialize the content moderator with CLIP model and processor.
        
        Args:
            clip_model: Pre-loaded CLIP model
            clip_processor: Pre-loaded CLIP processor
        """
        self.clip_model = clip_model
        self.clip_processor = clip_processor
        
        # Define inappropriate content categories and words
        self.inappropriate_content = {
            "violence": [
                "violence", "fight", "fighting", "attack", "assault", "battle", "war", "combat",
                "blood", "bloody", "gore", "injury", "wound", "bruise", "cut", "stab", "shoot",
                "gun", "rifle", "pistol", "weapon", "knife", "sword", "bomb", "explosion",
                "death", "dead", "corpse", "murder", "kill", "killing", "homicide"
            ],
            "sexual": [
                "nude", "naked", "sexual", "pornographic", "explicit", "adult content",
                "intimate", "provocative", "suggestive"
            ],
            "drugs": [
                "drugs", "cocaine", "heroin", "marijuana", "weed", "alcohol abuse",
                "substance abuse", "illegal drugs", "drug paraphernalia"
            ],
            "hate_speech": [
                "hate", "racist", "discrimination", "offensive", "slur", "bigotry",
                "extremist", "terrorist", "hate speech"
            ],
            "self_harm": [
                "self harm", "suicide", "cutting", "self injury", "self mutilation"
            ]
        }
        
        # Cache for text embeddings
        self.text_embeddings_cache = {}
        
        # Threshold for flagging content (cosine similarity)
        self.similarity_threshold = 0.25
        
    def get_text_embedding(self, text: str) -> np.ndarray:
        """
        Get CLIP embedding for a text string.
        
        Args:
            text: Text string to embed
            
        Returns:
            numpy array of the text embedding
        """
        # Check cache first
        if text in self.text_embeddings_cache:
            return self.text_embeddings_cache[text]
        
        # Process text through CLIP processor
        inputs = self.clip_processor(text=text, return_tensors="pt", padding=True, truncation=True)
        
        # Get text features from CLIP model
        with torch.no_grad():
            text_features = self.clip_model.get_text_features(**inputs)
        
        # Convert to numpy array and flatten
        embedding = text_features.numpy().flatten()
        
        # Cache the result
        self.text_embeddings_cache[text] = embedding
        
        return embedding
    
    def cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score between 0 and 1
        """
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        return float(similarity)
    
    def check_image_content(self, image_embedding: np.ndarray) -> Dict:
        """
        Check if an image embedding is similar to any inappropriate content.
        
        Args:
            image_embedding: Image embedding to check
            
        Returns:
            Dictionary with moderation results
        """
        results = {
            "flagged": False,
            "categories": {},
            "max_similarity": 0.0,
            "most_similar_content": None
        }
        
        max_similarity = 0.0
        most_similar_content = None
        
        # Check each category
        for category, words in self.inappropriate_content.items():
            category_max_similarity = 0.0
            category_most_similar = None
            
            for word in words:
                try:
                    text_embedding = self.get_text_embedding(word)
                    similarity = self.cosine_similarity(image_embedding, text_embedding)
                    
                    if similarity > category_max_similarity:
                        category_max_similarity = similarity
                        category_most_similar = word
                    
                    if similarity > max_similarity:
                        max_similarity = similarity
                        most_similar_content = word
                        
                except Exception as e:
                    print(f"Error processing word '{word}': {e}")
                    continue
            
            # Store category results
            results["categories"][category] = {
                "max_similarity": category_max_similarity,
                "most_similar_word": category_most_similar,
                "flagged": category_max_similarity > self.similarity_threshold
            }
        
        # Update overall results
        results["max_similarity"] = max_similarity
        results["most_similar_content"] = most_similar_content
        results["flagged"] = max_similarity > self.similarity_threshold
        
        return results
    
    def get_inappropriate_words(self) -> Dict[str, List[str]]:
        """
        Get the list of inappropriate words by category.
        
        Returns:
            Dictionary of categories and their associated words
        """
        return self.inappropriate_content
    
    def add_inappropriate_word(self, category: str, word: str):
        """
        Add a new inappropriate word to a category.
        
        Args:
            category: Category to add the word to
            word: Word to add
        """
        if category not in self.inappropriate_content:
            self.inappropriate_content[category] = []
        
        if word not in self.inappropriate_content[category]:
            self.inappropriate_content[category].append(word)
            # Clear cache since we added new content
            self.text_embeddings_cache.clear()
    
    def set_similarity_threshold(self, threshold: float):
        """
        Set the similarity threshold for flagging content.
        
        Args:
            threshold: New threshold value (0.0 to 1.0)
        """
        if 0.0 <= threshold <= 1.0:
            self.similarity_threshold = threshold
        else:
            raise ValueError("Threshold must be between 0.0 and 1.0")
    
    def save_moderation_results(self, results: Dict, filename: str):
        """
        Save moderation results to a JSON file.
        
        Args:
            results: Moderation results dictionary
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2) 