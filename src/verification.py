from datetime import datetime

class FactVerifier:
    def _init_(self):
        self.reliable_sources = [
            'bbc.com', 'reuters.com', 'apnews.com',
            'indianexpress.com', 'thehindu.com', 'ndtv.com'
        ]
    
    def verify_facts(self, facts):
        """
        Verify facts against reliable sources
        """
        verified_facts = []
        for fact in facts:
            verification_result = self.verify_single_fact(fact)
            verified_facts.append(verification_result)
        return verified_facts
    
    def verify_single_fact(self, fact):
        """
        Verify a single fact
        """
        # Extract fact statement from dict if necessary
        fact_text = fact['statement'] if isinstance(fact, dict) else fact
        
        # Extract key elements from fact
        entities = self.extract_key_elements(fact_text)
        
        # Search for corroborating sources
        sources = self.search_reliable_sources(entities)
        
        # Calculate credibility score
        credibility_score = self.calculate_credibility(sources)
        
        return {
            'fact': fact_text,
            'credibility_score': credibility_score,
            'sources': sources,
            'verification_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def extract_key_elements(self, fact):
        """
        Extract key elements from a fact
        """
        words = fact.split()
        return [word for word in words if word[0].isupper()]
    
    def search_reliable_sources(self, entities):
        """
        Search reliable sources for corroboration
        """
        return []
    
    def calculate_credibility(self, sources):
        """
        Calculate credibility score based on sources
        """
        if not sources:
            return 0.0
        return min(len(sources) * 0.2, 1.0)