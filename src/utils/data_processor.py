"""
Data Processing Module for Step 1: Exploration, Analysis and Anonymization

This module handles:
- Dataset loading and exploration
- Data anonymization using NER
- Comparison between original and anonymized data
- GDPR compliance documentation
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

from src.utils.anonymizer import TextAnonymizer


class DataProcessor:
    """
    Handles data processing for GDPR-compliant toxicity detection.
    """
    
    def __init__(self, data_dir: str = "./data"):
        """
        Initialize data processor.
        
        Args:
            data_dir: Base directory for data storage
        """
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.anonymized_dir = self.data_dir / "anonymized"
        
        # Create directories if they don't exist
        for directory in [self.raw_dir, self.processed_dir, self.anonymized_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.anonymizer = TextAnonymizer()
    
    def load_dataset(self, file_path: str) -> pd.DataFrame:
        """
        Load a dataset from file.
        
        Supports CSV, JSON, and TXT formats.
        
        Args:
            file_path: Path to the dataset file
        
        Returns:
            DataFrame with the loaded data
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset not found: {file_path}")
        
        # Load based on file extension
        if file_path.suffix == '.csv':
            df = pd.read_csv(file_path)
        elif file_path.suffix == '.json':
            df = pd.read_json(file_path)
        elif file_path.suffix == '.txt':
            # Assume one text per line
            with open(file_path, 'r', encoding='utf-8') as f:
                texts = [line.strip() for line in f if line.strip()]
            df = pd.DataFrame({'text': texts})
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        return df
    
    def explore_dataset(self, df: pd.DataFrame) -> Dict:
        """
        Perform exploratory data analysis on the dataset.
        
        Args:
            df: DataFrame to explore
        
        Returns:
            Dictionary with exploration statistics
        """
        stats = {
            "total_samples": len(df),
            "columns": list(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "sample_data": df.head(3).to_dict(orient='records')
        }
        
        # If 'text' column exists, analyze text statistics
        if 'text' in df.columns:
            text_lengths = df['text'].astype(str).str.len()
            stats["text_statistics"] = {
                "mean_length": float(text_lengths.mean()),
                "min_length": int(text_lengths.min()),
                "max_length": int(text_lengths.max()),
                "median_length": float(text_lengths.median())
            }
        
        return stats
    
    def anonymize_dataset(
        self,
        df: pd.DataFrame,
        text_column: str = 'text',
        method: str = 'mask'
    ) -> Tuple[pd.DataFrame, List[Dict]]:
        """
        Anonymize all texts in a dataset.
        
        Args:
            df: DataFrame containing texts to anonymize
            text_column: Name of the column containing text data
            method: Anonymization method (mask, pseudonymize, remove)
        
        Returns:
            Tuple of (anonymized_dataframe, metadata_list)
        """
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in dataset")
        
        anonymized_texts = []
        metadata_list = []
        
        print(f"Anonymizing {len(df)} texts using method: {method}")
        
        for idx, text in enumerate(df[text_column]):
            if pd.isna(text):
                anonymized_texts.append(text)
                metadata_list.append({"entities_found": 0, "entities": []})
                continue
            
            anon_text, metadata = self.anonymizer.anonymize(str(text), method)
            anonymized_texts.append(anon_text)
            metadata_list.append(metadata)
            
            if (idx + 1) % 100 == 0:
                print(f"Processed {idx + 1}/{len(df)} texts")
        
        # Create new dataframe with anonymized data
        df_anonymized = df.copy()
        df_anonymized[text_column] = anonymized_texts
        df_anonymized['anonymization_metadata'] = [json.dumps(m) for m in metadata_list]
        
        return df_anonymized, metadata_list
    
    def compare_datasets(
        self,
        df_original: pd.DataFrame,
        df_anonymized: pd.DataFrame,
        text_column: str = 'text'
    ) -> Dict:
        """
        Compare original and anonymized datasets.
        
        Args:
            df_original: Original dataset
            df_anonymized: Anonymized dataset
            text_column: Name of the text column
        
        Returns:
            Dictionary with comparison statistics
        """
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "sample_count": len(df_original),
            "anonymization_summary": {
                "total_entities_found": 0,
                "entity_types": {},
                "examples": []
            }
        }
        
        # Analyze anonymization metadata
        if 'anonymization_metadata' in df_anonymized.columns:
            for metadata_str in df_anonymized['anonymization_metadata']:
                metadata = json.loads(metadata_str)
                comparison["anonymization_summary"]["total_entities_found"] += metadata["entities_found"]
                
                for entity in metadata.get("entities", []):
                    entity_type = entity.get("type", "UNKNOWN")
                    comparison["anonymization_summary"]["entity_types"][entity_type] = \
                        comparison["anonymization_summary"]["entity_types"].get(entity_type, 0) + 1
        
        # Add examples
        for idx in range(min(3, len(df_original))):
            if text_column in df_original.columns:
                comparison["anonymization_summary"]["examples"].append({
                    "index": idx,
                    "original": str(df_original[text_column].iloc[idx])[:200],
                    "anonymized": str(df_anonymized[text_column].iloc[idx])[:200]
                })
        
        return comparison
    
    def save_dataset(self, df: pd.DataFrame, filename: str, output_dir: str = None):
        """
        Save a dataset to file.
        
        Args:
            df: DataFrame to save
            filename: Output filename
            output_dir: Output directory (uses anonymized_dir by default)
        """
        if output_dir is None:
            output_dir = self.anonymized_dir
        else:
            output_dir = Path(output_dir)
        
        output_path = output_dir / filename
        
        # Save based on file extension
        if filename.endswith('.csv'):
            df.to_csv(output_path, index=False)
        elif filename.endswith('.json'):
            df.to_json(output_path, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported file format: {filename}")
        
        print(f"Dataset saved to: {output_path}")
        return output_path
    
    def generate_data_processing_registry(
        self,
        comparison: Dict,
        output_file: str = "data_processing_registry.json"
    ) -> Path:
        """
        Generate GDPR data processing registry document.
        
        Args:
            comparison: Comparison data from compare_datasets
            output_file: Output filename
        
        Returns:
            Path to the generated registry file
        """
        registry = {
            "document_title": "Data Processing Registry - Digital Social Score",
            "created_at": datetime.now().isoformat(),
            "gdpr_compliance": {
                "legal_basis": "Legitimate interest in content moderation",
                "data_categories": [
                    "User-generated text content",
                    "Potentially toxic comments"
                ],
                "processing_purposes": [
                    "Toxicity detection",
                    "Content moderation",
                    "Safety scoring"
                ],
                "personal_data_handling": {
                    "collection": "Text content only, no direct identifiers",
                    "anonymization": "Automatic PII removal using NER",
                    "storage": "No personal data stored after processing",
                    "retention": "No data retention - immediate processing and disposal"
                }
            },
            "anonymization_process": {
                "method": "Named Entity Recognition (NER) using spaCy",
                "entities_removed": list(comparison["anonymization_summary"]["entity_types"].keys()),
                "statistics": comparison["anonymization_summary"]
            },
            "data_protection_measures": [
                "PII anonymization before model processing",
                "No logging of personal information",
                "Secure API endpoints with HTTPS (in production)",
                "Rate limiting to prevent abuse",
                "No data persistence after request completion"
            ],
            "data_subject_rights": {
                "right_to_access": "No personal data collected or stored",
                "right_to_erasure": "Not applicable - no data retention",
                "right_to_rectification": "Not applicable - no data retention",
                "right_to_data_portability": "Not applicable - no data retention",
                "right_to_object": "Users can opt-out of anonymization (not recommended)"
            },
            "data_breach_procedures": [
                "Immediate notification to data protection officer",
                "Assessment of breach scope and impact",
                "Notification to affected parties within 72 hours if required",
                "Documentation of breach and remediation steps"
            ],
            "responsible_parties": {
                "data_controller": "Organization using Digital Social Score API",
                "data_processor": "Digital Social Score API Service",
                "dpo_contact": "dpo@example.com (to be updated)"
            }
        }
        
        output_path = self.processed_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        print(f"Data processing registry saved to: {output_path}")
        return output_path


def process_sample_dataset():
    """
    Example function demonstrating the complete data processing workflow.
    """
    processor = DataProcessor()
    
    # Create sample dataset
    sample_texts = [
        "This is a normal comment about the weather.",
        "John Smith from New York posted this at john@example.com",
        "Call me at 555-123-4567 or visit 123 Main St, Boston",
        "Great product! Highly recommend it.",
        "This is terrible, I hate this stupid thing!"
    ]
    
    df_original = pd.DataFrame({'text': sample_texts, 'id': range(len(sample_texts))})
    
    # Save original
    original_path = processor.save_dataset(
        df_original,
        "sample_original.csv",
        processor.raw_dir
    )
    
    # Explore
    print("\n=== Dataset Exploration ===")
    stats = processor.explore_dataset(df_original)
    print(json.dumps(stats, indent=2))
    
    # Anonymize
    print("\n=== Anonymizing Dataset ===")
    df_anonymized, metadata = processor.anonymize_dataset(df_original, method='mask')
    
    # Save anonymized
    anonymized_path = processor.save_dataset(
        df_anonymized,
        "sample_anonymized.csv"
    )
    
    # Compare
    print("\n=== Comparing Datasets ===")
    comparison = processor.compare_datasets(df_original, df_anonymized)
    print(json.dumps(comparison, indent=2))
    
    # Generate registry
    print("\n=== Generating GDPR Registry ===")
    registry_path = processor.generate_data_processing_registry(comparison)
    
    print("\n=== Processing Complete ===")
    print(f"Original dataset: {original_path}")
    print(f"Anonymized dataset: {anonymized_path}")
    print(f"GDPR registry: {registry_path}")


if __name__ == "__main__":
    process_sample_dataset()
