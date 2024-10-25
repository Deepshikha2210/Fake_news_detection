from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
import numpy as np

class FakeNewsClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000)
        self.classifier = MultinomialNB()
        
    def train(self, texts, labels):
        X = self.vectorizer.fit_transform(texts)
        X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.2, random_state=42)
        self.classifier.fit(X_train, y_train)
        accuracy = self.classifier.score(X_test, y_test)
        print(f"Model trained with accuracy: {accuracy:.2f}")
        
    def predict(self, text):
        X = self.vectorizer.transform([text])
        probabilities = self.classifier.predict_proba(X)[0]
        classification = "REAL" if probabilities[1] < 0.5 else "FAKE"
        confidence = max(probabilities[0], probabilities[1])
        return {
            "classification": classification,
            "confidence": confidence,
            "fake_probability": probabilities[1],
            "real_probability": probabilities[0]
        }