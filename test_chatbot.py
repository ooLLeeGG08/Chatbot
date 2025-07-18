#!/usr/bin/env python3
"""
Simple test script for the chatbot
Run this to test the chatbot functionality
"""

import requests
import time

def test_chatbot(query, server_url="http://localhost:8080"):
    """Test the chatbot with a given query"""
    try:
        print(f"Testing query: '{query}'")
        response = requests.post(server_url, data=query, timeout=30)
        
        if response.status_code == 200:
            answer = response.text
            print(f"Answer: {answer}")
            return answer
        else:
            print(f"Error: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("🤖 Chatbot Test Script")
    print("=" * 40)
    
    # Test queries
    test_queries = [
        "What is Python?",
        "JavaScript programming",
        "What is machine learning?",
        "How does the internet work?"
    ]
    
    for query in test_queries:
        test_chatbot(query)
        print("-" * 40)
        time.sleep(2)  # Delay between requests
    
    print("\n✅ Testing complete!")
    print("You can now open http://localhost:8080 in your browser")
    print("to use the interactive web interface.")