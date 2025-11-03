"""
Example: Using the Digital Social Score API

This script demonstrates how to use the API for toxicity detection.
"""

import requests
import json


def test_api_connection(base_url="http://localhost:8000"):
    """Test if the API is running."""
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✓ API is running")
            print(f"  Status: {response.json()}")
            return True
        else:
            print("✗ API returned error:", response.status_code)
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Make sure it's running:")
        print("  uvicorn src.api.main:app --reload")
        return False


def analyze_single_text(text, base_url="http://localhost:8000", anonymize=True):
    """Analyze a single text for toxicity."""
    print(f"\nAnalyzing: '{text}'")
    
    response = requests.post(
        f"{base_url}/analyze",
        json={
            "text": text,
            "anonymize": anonymize,
            "anonymization_method": "mask"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"  Toxicity Score: {result['toxicity_score']}")
        print(f"  Is Toxic: {result['is_toxic']}")
        print(f"  Severity: {result['severity']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Processing Time: {result['processing_time_ms']}ms")
        
        if result['categories']:
            print("  Category Scores:")
            for category, score in result['categories'].items():
                if score > 0:
                    print(f"    - {category}: {score}")
        
        return result
    else:
        print(f"  Error: {response.status_code}")
        print(f"  {response.text}")
        return None


def analyze_batch(texts, base_url="http://localhost:8000"):
    """Analyze multiple texts at once."""
    print(f"\nBatch analyzing {len(texts)} texts...")
    
    response = requests.post(
        f"{base_url}/analyze/batch",
        json={
            "texts": texts,
            "anonymize": True
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Analyzed {result['count']} texts")
        print(f"  Total processing time: {result['total_processing_time_ms']}ms")
        
        for i, text_result in enumerate(result['results']):
            print(f"\n  Text {i+1}: {texts[i][:50]}...")
            print(f"    Score: {text_result['toxicity_score']}, Toxic: {text_result['is_toxic']}")
        
        return result
    else:
        print(f"Error: {response.status_code}")
        return None


def main():
    """Main demonstration."""
    print("=" * 70)
    print("Digital Social Score API - Usage Examples")
    print("=" * 70)
    
    base_url = "http://localhost:8000"
    
    # Test connection
    print("\n1. Testing API Connection...")
    if not test_api_connection(base_url):
        return
    
    # Example 1: Non-toxic text
    print("\n2. Example 1: Non-toxic text")
    analyze_single_text(
        "This is a wonderful day! I love learning new things.",
        base_url
    )
    
    # Example 2: Potentially toxic text
    print("\n3. Example 2: Potentially toxic text")
    analyze_single_text(
        "This is terrible, I hate it!",
        base_url
    )
    
    # Example 3: Text with personal information
    print("\n4. Example 3: Text with personal information (anonymized)")
    analyze_single_text(
        "Contact John Smith at john@example.com for details.",
        base_url,
        anonymize=True
    )
    
    # Example 4: Batch analysis
    print("\n5. Example 4: Batch analysis")
    test_texts = [
        "Great product, highly recommended!",
        "This is the worst thing I've ever seen!",
        "Neutral comment about the weather.",
        "I hate this stupid thing!"
    ]
    analyze_batch(test_texts, base_url)
    
    # Example 5: GDPR compliance info
    print("\n6. Example 5: GDPR Compliance Information")
    response = requests.get(f"{base_url}/gdpr/compliance")
    if response.status_code == 200:
        gdpr_info = response.json()
        print(f"  GDPR Compliant: {gdpr_info['compliant']}")
        print(f"  Data Storage: {gdpr_info['data_processing']['personal_data_storage']}")
        print(f"  Available Methods: {', '.join(gdpr_info['anonymization_methods'])}")
    
    print("\n" + "=" * 70)
    print("✓ All examples completed!")
    print("\nFor interactive documentation, visit:")
    print(f"  {base_url}/docs")
    print("=" * 70)


if __name__ == "__main__":
    main()
