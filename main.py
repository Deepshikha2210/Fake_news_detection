from src.scrapper import NewsSourceVerifier
from src.text_analysis import TextAnalyzer,analyze_text
from src.cleaner import TextCleaner
from src.verification import FactVerifier  # Import the FactVerifier class
from datetime import datetime
from typing import Dict, Any, List

def process_input(input_text: str) -> Dict[str, Any]:
    try:
        print("Analyzing headline and searching related articles...")
        
        # Initialize components
        text_cleaner = TextCleaner()
        fact_verifier = FactVerifier()  # Initialize FactVerifier
        analyzer =TextAnalyzer() 
        
        # Clean and analyze the input text
        cleaned_text = text_cleaner.clean_text(input_text)
        analysis_result = analyze_text(cleaned_text)
        
        # Extract entities and important phrases
        entities = analyzer.extract_entities(cleaned_text)
        important_phrases = text_cleaner.get_important_phrases(cleaned_text)
        
        # Search for related articles
        news_verifier = NewsSourceVerifier()
        related_articles = news_verifier.search_related_articles(cleaned_text)
        
        # Analyze related articles
        article_facts = []
        article_analyses = []
        for article in related_articles:
            if article.get('content'):
                cleaned_article = text_cleaner.clean_text(article['content'])
                article_analysis = analyze_text(cleaned_article)
                article_summary = analyzer.summarize_text(cleaned_article)
                article_sentiment = analyzer.analyze_sentiment(cleaned_article)
                article_entities = analyzer.extract_entities(cleaned_article)
                article_analyses.append({
                    'source': article['source'],
                    'summary': article_summary,
                    'sentiment': article_sentiment,
                    'entities': article_entities
                })
                if article_analysis and 'facts' in article_analysis:
                    for fact in article_analysis['facts']:
                        article_facts.append({
                            'statement': fact['statement'],
                            'confidence': fact.get('confidence', 0.5) * article['credibility_score'],
                            'source': article['source']
                        })
        
        # Verify all facts using FactVerifier
        all_facts = analysis_result['facts'] + article_facts
        verified_facts = fact_verifier.verify_facts(all_facts)
        
        # Calculate metrics
        overall_credibility = (
            sum(fact['credibility_score'] for fact in verified_facts) / len(verified_facts)
            if verified_facts else 0
        )
        
        unique_sources = len(set(article['source'] for article in related_articles))
        source_diversity_score = (
            min(unique_sources / len(news_verifier.trusted_sources), 1.0)
            if news_verifier.trusted_sources else 0
        )
        
        return {
            "summary": analysis_result['summary'],
            "sentiment": analysis_result['sentiment'],
            "entities": analysis_result['entities'],
            "important_phrases": important_phrases,
            "verified_facts": verified_facts,
            "related_articles": related_articles,
            "article_analyses": article_analyses,
            "verification_details": {
                "total_facts": len(verified_facts),
                "avg_credibility": overall_credibility,
                "source_diversity_score": source_diversity_score,
                "total_sources_found": unique_sources,
                "verification_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
    except Exception as e:
        print(f"Debug - Error details: {str(e)}")
        return {"error": f"An error occurred: {str(e)}"}

def display_result(result: Dict[str, Any]):
    print("\n===== News Verification Result =====")
    
    if "error" in result:
        print(f"\nError: {result['error']}")
        return
    
    try:
        print(f"\nHeadline Analysis:")
        print(f"Summary: {result['summary']}")
        print(f"Sentiment: {result['sentiment']:.2f} (-1 very negative, 1 very positive)")
        
        if result['entities']:
            print("\nIdentified Entities:")
            for entity, entity_type in result['entities']:
                print(f"- {entity} ({entity_type})")

        if result['important_phrases']:
            print("\nImportant Phrases:")
            for phrase in result['important_phrases']:
                print(f"- {phrase}")
        
        if result['verification_details']:
            print(f"\nVerification Details:")
            print(f"- Total facts checked: {result['verification_details']['total_facts']}")
            print(f"- Average credibility score: {result['verification_details']['avg_credibility']:.2f}")
            print(f"- Source diversity score: {result['verification_details']['source_diversity_score']:.2f}")
            print(f"- Total sources found: {result['verification_details']['total_sources_found']}")
            print(f"- Verification time: {result['verification_details']['verification_timestamp']}")
        
        if result['related_articles']:
            print("\nRelated Articles from Trusted Sources:")
            for idx, article in enumerate(result['related_articles'], 1):
                print(f"\n{idx}. {article['title']}")
                print(f"   Source: {article['source']} (Credibility: {article['credibility_score']:.2f})")
                print(f"   URL: {article['url']}")
        
        if result['verified_facts']:
            print("\nVerified Facts:")
            for idx, fact in enumerate(result['verified_facts'][:3], 1):
                print(f"{idx}. {fact['fact']}")
                print(f"   Credibility: {fact['credibility_score']:.2f}")
                
        print("\nNote: This system provides an initial assessment. Always cross-verify information from multiple reliable sources.")
        
    except Exception as e:
        print(f"\nError displaying results: {e}")

if __name__ == "__main__":
    try:
        user_input = input("Enter a news headline to verify: ")
        result = process_input(user_input)
        display_result(result)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")