#!/usr/bin/env python3
"""
Test script for content moderation functionality.
This script demonstrates how to use the ContentModerator class.
"""

import numpy as np
import torch
from transformers.models.clip.processing_clip import CLIPProcessor
from transformers.models.clip.modeling_clip import CLIPModel
from content_moderator import ContentModerator
from PIL import Image
import json

def test_text_embeddings():
    """Test text embedding generation for inappropriate words."""
    print("=== Testing Text Embeddings ===")
    
    # Load CLIP model
    print("Loading CLIP model...")
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    
    # Initialize content moderator
    moderator = ContentModerator(clip_model, clip_processor)
    
    # Test some inappropriate words
    test_words = ["violence", "gun", "blood", "nude", "drugs", "hate"]
    
    print("\nTesting text embeddings for inappropriate words:")
    for word in test_words:
        embedding = moderator.get_text_embedding(word)
        print(f"  '{word}': {embedding.shape} - {embedding[:5]}...")
    
    # Test similarity between related words
    print("\nTesting similarity between related words:")
    violence_emb = moderator.get_text_embedding("violence")
    gun_emb = moderator.get_text_embedding("gun")
    peace_emb = moderator.get_text_embedding("peace")
    
    violence_gun_sim = moderator.cosine_similarity(violence_emb, gun_emb)
    violence_peace_sim = moderator.cosine_similarity(violence_emb, peace_emb)
    
    print(f"  'violence' vs 'gun': {violence_gun_sim:.3f}")
    print(f"  'violence' vs 'peace': {violence_peace_sim:.3f}")
    
    return moderator

def test_content_checking(moderator):
    """Test content checking with sample embeddings."""
    print("\n=== Testing Content Checking ===")
    
    # Create a sample embedding (this would normally come from an image)
    # We'll use a random embedding for demonstration
    sample_embedding = np.random.randn(512)  # CLIP embeddings are 512-dimensional
    sample_embedding = sample_embedding / np.linalg.norm(sample_embedding)  # Normalize
    
    print("Testing content checking with sample embedding...")
    results = moderator.check_image_content(sample_embedding)
    
    print(f"Overall flagged: {results['flagged']}")
    print(f"Max similarity: {results['max_similarity']:.3f}")
    print(f"Most similar content: '{results['most_similar_content']}'")
    
    print("\nCategory breakdown:")
    for category, details in results["categories"].items():
        status = "⚠️ FLAGGED" if details["flagged"] else "✓ OK"
        print(f"  {category}: {status} (similarity: {details['max_similarity']:.3f})")
    
    return results

def test_threshold_adjustment(moderator):
    """Test how changing the threshold affects flagging."""
    print("\n=== Testing Threshold Adjustment ===")
    
    # Create a sample embedding
    sample_embedding = np.random.randn(512)
    sample_embedding = sample_embedding / np.linalg.norm(sample_embedding)
    
    thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]
    
    for threshold in thresholds:
        moderator.set_similarity_threshold(threshold)
        results = moderator.check_image_content(sample_embedding)
        print(f"Threshold {threshold}: {'FLAGGED' if results['flagged'] else 'OK'} (max sim: {results['max_similarity']:.3f})")

def test_custom_words(moderator):
    """Test adding custom inappropriate words."""
    print("\n=== Testing Custom Words ===")
    
    # Add some custom words
    moderator.add_inappropriate_word("violence", "knife attack")
    moderator.add_inappropriate_word("violence", "street fight")
    moderator.add_inappropriate_word("custom", "inappropriate content")
    
    print("Added custom words. Current categories:")
    for category, words in moderator.get_inappropriate_words().items():
        print(f"  {category}: {len(words)} words")
        if category == "custom":
            print(f"    Custom words: {words}")

def main():
    """Run all tests."""
    print("Content Moderation Test Suite")
    print("=" * 40)
    
    try:
        # Test 1: Text embeddings
        moderator = test_text_embeddings()
        
        # Test 2: Content checking
        test_content_checking(moderator)
        
        # Test 3: Threshold adjustment
        test_threshold_adjustment(moderator)
        
        # Test 4: Custom words
        test_custom_words(moderator)
        
        print("\n" + "=" * 40)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 