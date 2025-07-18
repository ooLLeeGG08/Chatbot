import requests
import string
from lxml import html
from googlesearch import search
from bs4 import BeautifulSoup
import time

def chatbot_query(query, index=0):
    fallback = 'Sorry, I could not find information about that right now. Please try rephrasing your question or try again later.'
    result = ''

    try:
        # Add a small delay to avoid rate limiting
        time.sleep(1)
        
        # Get search results
        search_result_list = list(search(query, num_results=3, sleep_interval=1))
        
        if len(search_result_list) == 0:
            return fallback
            
        if index >= len(search_result_list):
            index = 0
        
        url = search_result_list[index]

        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        page = requests.get(url, headers=headers, timeout=10)

        if page.status_code != 200:
            return fallback

        soup = BeautifulSoup(page.content, features="lxml")

        # Try to extract text from paragraphs
        article_text = ''
        articles = soup.findAll('p')
        
        for element in articles:
            text = ''.join(element.findAll(text=True))
            if len(text.strip()) > 20:  # Only add substantial text
                article_text += ' ' + text.strip()
                
        if len(article_text.strip()) < 10:
            return fallback
            
        # Clean up the text
        article_text = article_text.replace('\n', ' ').replace('\r', ' ')
        
        # Get first meaningful sentence
        sentences = article_text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            # Filter out common non-content text
            skip_phrases = ['javascript', 'cookie', 'privacy', 'notice:', 'advertisement', 
                          'subscribe', 'follow us', 'sign up', 'newsletter', 'terms of service',
                          'please enable', 'browser', 'cookies']
            
            if (len(sentence) > 30 and 
                not sentence.startswith('©') and 
                not any(phrase in sentence.lower() for phrase in skip_phrases) and
                not sentence.startswith('Please ') and
                not sentence.startswith('We use ') and
                sentence.count(' ') > 4):  # Ensure it's a substantial sentence
                result = sentence
                break
        
        if not result:
            # If no good sentence found, try the first part
            words = article_text.split()
            if len(words) > 10:
                result = ' '.join(words[:20]) + '...'
        
        if len(result.strip()) > 0:
            return result
        else:
            return fallback

    except Exception as e:
        return fallback
