#!/usr/bin/env python3
"""
Simple script to change the content moderation threshold.
Usage: python change_threshold.py 0.25
"""

import sys
import re

def change_threshold(new_threshold):
    """Change the threshold in content_moderator.py"""
    
    # Validate threshold
    try:
        threshold_value = float(new_threshold)
        if not (0.0 <= threshold_value <= 1.0):
            print("Error: Threshold must be between 0.0 and 1.0")
            return False
    except ValueError:
        print("Error: Threshold must be a number")
        return False
    
    # Read the file
    file_path = "content_moderator.py"
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return False
    
    # Replace the threshold
    old_pattern = r'self\.similarity_threshold = \d+\.\d+'
    new_line = f'self.similarity_threshold = {threshold_value}'
    
    if re.search(old_pattern, content):
        new_content = re.sub(old_pattern, new_line, content)
        
        # Write back to file
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        print(f"✅ Threshold changed to {threshold_value}")
        return True
    else:
        print("Error: Could not find threshold line in content_moderator.py")
        return False

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python change_threshold.py <threshold>")
        print("Example: python change_threshold.py 0.25")
        print("Example: python change_threshold.py 0.3")
        return
    
    new_threshold = sys.argv[1]
    success = change_threshold(new_threshold)
    
    if success:
        print("\nNext steps:")
        print("1. Run combined_processor.py to process videos with new threshold")
        print("2. Check the results to see if the threshold works well")
        print("3. Adjust if needed using this script again")

if __name__ == "__main__":
    main() 