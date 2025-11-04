"""
Example: Step 1 - Data Exploration, Analysis and Anonymization

This script demonstrates the complete workflow for:
1. Loading a dataset
2. Exploring the data
3. Anonymizing personal information using NER
4. Comparing original vs anonymized data
5. Generating GDPR data processing registry

As required by the problem statement.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.data_processor import DataProcessor
import pandas as pd
import json


def demonstrate_anonymization():
    """Demonstrate the complete anonymization workflow."""
    
    print("=" * 70)
    print("Step 1: Data Exploration, Analysis and Anonymization")
    print("=" * 70)
    print()
    
    # Initialize processor
    print("1. Initializing Data Processor...")
    processor = DataProcessor(data_dir="./data")
    print("✓ Processor initialized")
    print()
    
    # Create sample dataset with PII
    print("2. Creating Sample Dataset with Personal Information...")
    sample_data = {
        'id': range(1, 11),
        'text': [
            "This is a great product! Highly recommend it.",
            "Contact John Smith at john.smith@example.com for more details.",
            "Call me at 555-123-4567 or visit our office in New York.",
            "Meeting scheduled with Marie Dupont on January 15th, 2024.",
            "Please send documents to info@company.org by next week.",
            "Visit our website at 192.168.1.1 for more information.",
            "Dr. Sarah Johnson from Boston General Hospital will attend.",
            "The event will be held at Microsoft headquarters in Seattle.",
            "Terrible service! I hate this stupid thing, complete waste of money!",
            "Amazing experience, loved every moment of it!"
        ],
        'category': ['positive', 'neutral', 'neutral', 'neutral', 'neutral', 
                     'neutral', 'neutral', 'neutral', 'negative', 'positive']
    }
    
    df_original = pd.DataFrame(sample_data)
    print(f"✓ Created dataset with {len(df_original)} samples")
    print()
    
    # Save original dataset
    print("3. Saving Original Dataset...")
    original_path = processor.save_dataset(
        df_original, 
        "example_original.csv",
        processor.raw_dir
    )
    print(f"✓ Saved to: {original_path}")
    print()
    
    # Explore dataset
    print("4. Exploring Dataset...")
    stats = processor.explore_dataset(df_original)
    print(json.dumps(stats, indent=2))
    print()
    
    # Anonymize using different methods
    print("5. Anonymizing Dataset (Method: mask)...")
    df_anonymized_mask, metadata_mask = processor.anonymize_dataset(
        df_original,
        text_column='text',
        method='mask'
    )
    print(f"✓ Anonymized {len(df_anonymized_mask)} texts")
    print()
    
    # Show examples of anonymization
    print("6. Comparing Original vs Anonymized (Examples)...")
    print("-" * 70)
    for idx in range(min(5, len(df_original))):
        print(f"\nExample {idx + 1}:")
        print(f"  Original:    {df_original['text'].iloc[idx]}")
        print(f"  Anonymized:  {df_anonymized_mask['text'].iloc[idx]}")
        
        # Show detected entities
        metadata = json.loads(df_anonymized_mask['anonymization_metadata'].iloc[idx])
        if metadata['entities_found'] > 0:
            print(f"  Entities found: {metadata['entities_found']}")
            for entity in metadata['entities'][:3]:  # Show first 3
                print(f"    - {entity['type']}: '{entity['text']}'")
    print("-" * 70)
    print()
    
    # Save anonymized dataset
    print("7. Saving Anonymized Dataset...")
    anonymized_path = processor.save_dataset(
        df_anonymized_mask,
        "example_anonymized_mask.csv"
    )
    print(f"✓ Saved to: {anonymized_path}")
    print()
    
    # Try pseudonymization method
    print("8. Anonymizing with Pseudonymization Method...")
    df_anonymized_pseudo, _ = processor.anonymize_dataset(
        df_original,
        text_column='text',
        method='pseudonymize'
    )
    pseudo_path = processor.save_dataset(
        df_anonymized_pseudo,
        "example_anonymized_pseudo.csv"
    )
    print(f"✓ Saved to: {pseudo_path}")
    print()
    
    # Compare datasets
    print("9. Generating Comparison Statistics...")
    comparison = processor.compare_datasets(df_original, df_anonymized_mask)
    print(json.dumps(comparison, indent=2, default=str))
    print()
    
    # Generate GDPR registry
    print("10. Generating GDPR Data Processing Registry...")
    registry_path = processor.generate_data_processing_registry(comparison)
    print(f"✓ Registry saved to: {registry_path}")
    print()
    
    # Summary
    print("=" * 70)
    print("Summary of Step 1 Completion")
    print("=" * 70)
    print(f"✓ Original dataset: {original_path}")
    print(f"✓ Anonymized dataset (mask): {anonymized_path}")
    print(f"✓ Anonymized dataset (pseudo): {pseudo_path}")
    print(f"✓ GDPR registry: {registry_path}")
    print()
    print(f"Total entities anonymized: {comparison['anonymization_summary']['total_entities_found']}")
    print("Entity types found:")
    for entity_type, count in comparison['anonymization_summary']['entity_types'].items():
        print(f"  - {entity_type}: {count}")
    print()
    print("Step 1 - Data Anonymization Complete! ✓")
    print("=" * 70)


def demonstrate_api_usage():
    """Demonstrate using the anonymizer directly."""
    
    print("\n\n")
    print("=" * 70)
    print("Bonus: Direct Anonymizer Usage")
    print("=" * 70)
    print()
    
    from src.utils.anonymizer import TextAnonymizer
    
    try:
        anonymizer = TextAnonymizer()
        
        test_texts = [
            "Contact John at john@example.com",
            "Call 555-1234 for assistance",
            "Meet at Apple headquarters in Cupertino"
        ]
        
        print("Testing different anonymization methods:\n")
        
        for text in test_texts:
            print(f"Original: {text}")
            
            for method in ['mask', 'pseudonymize', 'remove']:
                anonymized, metadata = anonymizer.anonymize(text, method=method)
                print(f"  {method:15s}: {anonymized}")
            
            print()
        
        print("✓ Direct anonymizer usage demonstrated")
        
    except OSError as e:
        print(f"Note: spaCy model not installed. Install with:")
        print("  python -m spacy download en_core_web_sm")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Digital Social Score - Step 1 Demonstration".center(68) + "║")
    print("║" + "  Data Exploration, Analysis and Anonymization".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    try:
        demonstrate_anonymization()
        demonstrate_api_usage()
        
        print("\n✓ All demonstrations completed successfully!")
        print("\nNext steps:")
        print("  1. Review the generated files in the data/ directory")
        print("  2. Check the GDPR registry in data/processed/")
        print("  3. Start the API: uvicorn src.api.main:app --reload")
        print("  4. Test API: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"\n✗ Error during demonstration: {e}")
        print("\nMake sure to install dependencies first:")
        print("  pip install -r requirements.txt")
        print("  python -m spacy download en_core_web_sm")
        sys.exit(1)
