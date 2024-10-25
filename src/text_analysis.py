from typing import Dict, Any, List, Tuple
import re
from datetime import datetime
import spacy
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords
import nltk

class TextAnalyzer:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.name_patterns = [
            r'([A-Z][a-z]+ [A-Z][a-z]+)',  # Basic name pattern
            r'Mr\. [A-Z][a-z]+',
            r'Mrs\. [A-Z][a-z]+',
            r'Dr\. [A-Z][a-z]+'
        ]
        
        self.date_patterns = [
            r'\d{1,2} [A-Za-z]+ \d{4}',
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{4}-\d{2}-\d{2}'
        ]
        
        # Download stopwords if not already downloaded
        nltk.download('stopwords', quiet=True)
        self.stop_words = set(stopwords.words('english'))

    

    def summarize_text(self, text: str, num_sentences: int = 3) -> str:
        # Tokenize the text into sentences
        sentences = sent_tokenize(text)

        # Tokenize words and remove stopwords
        words = word_tokenize(text.lower())
        word_frequencies = FreqDist(word for word in words if word not in self.stop_words)

        # Calculate sentence scores based on word frequencies
        sentence_scores = {}
        for sentence in sentences:
            for word in word_tokenize(sentence.lower()):
                if word in word_frequencies:
                    if sentence not in sentence_scores:
                        sentence_scores[sentence] = word_frequencies[word]
                    else:
                        sentence_scores[sentence] += word_frequencies[word]

        # Get the top N sentences with the highest scores
        summary_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]

        # Sort the selected sentences based on their original order in the text
        summary_sentences = [sentence for sentence in sentences if sentence in summary_sentences]

        # Join the sentences to create the summary
        summary = ' '.join(summary_sentences)

        return summary
    
    def extract_entities(self, text: str) -> List[Tuple[str, str]]:
        entities = []
        doc = self.nlp(text)
        for ent in doc.ents:
            entities.append((ent.text, ent.label_))
        # Extract names
        for pattern in self.name_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                entities.append((match, 'PERSON'))
        
        # Extract dates
        for pattern in self.date_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                entities.append((match, 'DATE'))
        
        # Extract numbers/age
        age_matches = re.findall(r'\b\d+\s+(?:year|years|yr|yrs)(?:\s+old)?\b', text, re.IGNORECASE)
        for match in age_matches:
            entities.append((match, 'AGE'))
        
        return entities

    def analyze_sentiment(self, text: str) -> float:
        # Simple sentiment analysis based on keywords
        positive_words = {'good', 'great', 'excellent', 'positive', 'success', 'happy', 'win', 'wins', 'achieve'}
        negative_words = {'bad', 'poor', 'negative', 'sad', 'death', 'dies', 'kill', 'killed', 'accident', 'crash'}
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count == 0 and negative_count == 0:
            return 0.0
        
        total = positive_count + negative_count
        return (positive_count - negative_count) / total

    def extract_facts(self, text: str) -> List[Dict[str, Any]]:
        facts = []
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                # Extract entities in this sentence
                entities = self.extract_entities(sentence)
                if entities:
                    facts.append({
                        'statement': sentence,
                        'entities': entities,
                        'confidence': 0.7
                    })
        
        return facts

def analyze_text(text: str) -> Dict[str, Any]:
    analyzer = TextAnalyzer()
    
    # Basic text cleanup
    text = text.strip()
    
    # Perform analysis
    entities = analyzer.extract_entities(text)
    sentiment = analyzer.analyze_sentiment(text)
    facts = analyzer.extract_facts(text)
    
    return {
        'summary': text,
        'sentiment': sentiment,
        'entities': entities,
        'facts': facts
    }