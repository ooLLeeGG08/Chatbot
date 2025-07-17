import requests
import string
import time
from lxml import html
from googlesearch import search
from bs4 import BeautifulSoup

def chatbot_query(query, index=0):
    fallback = 'Sorry, I cannot find a good answer for that question.'
    result = ''

    try:
        # Input validation
        if not query or not query.strip():
            return "Please ask me a question!"
        
        print(f"Searching for: {query}")
        
        # Get search results
        search_result_list = list(search(query, num=5, stop=3, pause=1))
        
        if not search_result_list:
            return "Sorry, I couldn't find any search results for your question."
        
        # Try multiple search results if the first one fails
        for i in range(min(len(search_result_list), 3)):
            try:
                url = search_result_list[i]
                print(f"Trying URL: {url}")
                
                # Set headers to avoid being blocked
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                page = requests.get(url, headers=headers, timeout=10)
                page.raise_for_status()
                
                soup = BeautifulSoup(page.content, features="lxml")
                
                # Try to extract meaningful text
                article_text = ''
                
                # Look for paragraphs
                paragraphs = soup.find_all('p')
                for p in paragraphs:
                    text = p.get_text().strip()
                    if len(text) > 20:  # Only add substantial paragraphs
                        article_text += ' ' + text
                        if len(article_text) > 500:  # Limit text length
                            break
                
                # Clean up the text
                article_text = article_text.strip()
                
                if article_text:
                    # Get first meaningful sentence
                    sentences = article_text.split('.')
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if len(sentence) > 30 and not sentence.startswith(('http', 'www')):
                            # Remove excessive whitespace
                            sentence = ' '.join(sentence.split())
                            if sentence:
                                return sentence + '.'
                    
                    # If no good sentence found, return first part of text
                    if len(article_text) > 100:
                        return article_text[:200].strip() + '...'
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {url}: {e}")
                continue
            except Exception as e:
                print(f"Error processing {url}: {e}")
                continue
        
        return fallback
        
    except Exception as e:
        print(f"Search error: {e}")
        return fallback
