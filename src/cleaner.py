import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import spacy

class TextCleaner:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.stop_words = set(stopwords.words('english'))
    
    def clean_text(self, text):
        """
        Clean and preprocess the input text
        """
        if not text:
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # Remove special characters and digits
        text = re.sub(r'[^\w\s]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    """def extract_entities(self, text):
    
        Extract named entities from text using SpaCy
        
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append((ent.text, ent.label_))
            
        return entities"""
    
    def get_important_phrases(self, text):
        """
        Extract important phrases from text
        """
        doc = self.nlp(text)
        important_phrases = []
        
        for chunk in doc.noun_chunks:
            if chunk.root.pos_ in ['NOUN', 'PROPN']:
                important_phrases.append(chunk.text)
                
        return important_phrases
       

def clean_text(text):
    cleaner = TextCleaner()
    return cleaner.clean_text(text)