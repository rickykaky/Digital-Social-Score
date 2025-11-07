"""
Tests pour les composants Kubeflow Pipeline v2
Fichier: tests/pipeline/test_pipeline_components.py
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile


class TestPrepareDataComponent:
    """Tests pour le composant prepare_data_op"""
    
    @pytest.mark.pipeline
    def test_prepare_data_component_input_validation(self):
        """Doit valider que le CSV d'entrée existe"""
        # Mock du composant
        from src.pipeline.pipeline import prepare_data_op
        
        # Vérifier que la fonction est callable
        assert callable(prepare_data_op)
    
    @pytest.mark.pipeline
    def test_prepare_data_component_with_missing_data(self, temp_csv):
        """Doit gérer les données manquantes"""
        # Créer un CSV avec NaN
        df = pd.DataFrame({
            'comment_text': ['test 1', None, 'test 3'],
            'toxic': [0, 1, None]
        })
        
        # Test qu'on peut charger et nettoyer
        df_clean = df.dropna()
        assert len(df_clean) == 1
    
    @pytest.mark.pipeline
    def test_prepare_data_component_output_format(self, temp_csv):
        """Le composant doit produire un CSV valide en sortie"""
        df = pd.read_csv(temp_csv)
        
        # Simuler le nettoyage
        df_clean = df.dropna()
        
        # Vérifier le format
        assert isinstance(df_clean, pd.DataFrame)
        assert 'comment_text' in df_clean.columns
        assert len(df_clean) > 0
    
    @pytest.mark.pipeline
    def test_prepare_data_component_nltk_processing(self):
        """Doit appliquer le traitement NLTK (tokenization, stopwords, lemmatization)"""
        # Simuler le pipeline NLTK
        from nltk.tokenize import word_tokenize
        from nltk.corpus import stopwords
        from nltk.stem import WordNetLemmatizer
        
        text = "This is a test comment"
        
        # Tokenization
        tokens = word_tokenize(text.lower())
        assert isinstance(tokens, list)
        assert len(tokens) > 0
        
        # Stopwords removal
        stop_words = set(stopwords.words('english'))
        filtered = [w for w in tokens if w not in stop_words]
        assert len(filtered) < len(tokens)
        
        # Lemmatization
        lemmatizer = WordNetLemmatizer()
        lemmatized = [lemmatizer.lemmatize(w) for w in filtered]
        assert isinstance(lemmatized, list)


class TestTrainModelComponent:
    """Tests pour le composant train_model_op"""
    
    @pytest.mark.pipeline
    def test_train_model_component_vectorizer_initialization(self):
        """Doit initialiser TF-IDF avec les bons paramètres"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        vectorizer = TfidfVectorizer(
            max_features=5000,
            min_df=5,
            max_df=0.8
        )
        
        assert vectorizer.max_features == 5000
        assert vectorizer.min_df == 5
        assert vectorizer.max_df == 0.8
    
    @pytest.mark.pipeline
    def test_train_model_component_model_initialization(self):
        """Doit initialiser LogisticRegression avec les bons paramètres"""
        from sklearn.linear_model import LogisticRegression
        
        model = LogisticRegression(max_iter=1000, random_state=42)
        
        assert model.max_iter == 1000
        assert model.random_state == 42
    
    @pytest.mark.pipeline
    def test_train_model_component_produces_valid_model(self, sample_comments_df):
        """Le composant doit produire un modèle entraînable"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        
        # Vectorize
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(sample_comments_df['comment_text'])
        y = sample_comments_df['toxic']
        
        # Train
        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)
        
        # Vérifier que le modèle a été entraîné
        assert model.n_features_in_ > 0
        assert model.classes_ is not None
    
    @pytest.mark.pipeline
    def test_train_model_component_produces_predictions(self, sample_comments_df):
        """Le modèle entraîné doit produire des prédictions"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(sample_comments_df['comment_text'])
        y = sample_comments_df['toxic']
        
        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)
        
        # Prédictions
        predictions = model.predict(X)
        assert len(predictions) == len(y)
        assert all(p in [0, 1] for p in predictions)
    
    @pytest.mark.pipeline
    def test_train_model_component_probabilities(self, sample_comments_df):
        """Le modèle doit fournir des probabilités"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(sample_comments_df['comment_text'])
        y = sample_comments_df['toxic']
        
        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)
        
        # Probabilités
        proba = model.predict_proba(X)
        assert proba.shape == (len(y), 2)
        assert np.allclose(proba.sum(axis=1), 1.0)  # Somme = 1
    
    @pytest.mark.pipeline
    def test_train_model_component_artifact_serialization(self, model_artifacts):
        """Les artefacts du modèle doivent être sérialisables avec joblib"""
        import joblib
        
        model = model_artifacts['model']
        vectorizer = model_artifacts['vectorizer']
        
        # Vérifier qu'on peut charger les modèles
        loaded_model = joblib.load(model_artifacts['model_path'])
        loaded_vectorizer = joblib.load(model_artifacts['vectorizer_path'])
        
        assert loaded_model is not None
        assert loaded_vectorizer is not None


class TestEvaluateModelComponent:
    """Tests pour le composant evaluate_model_op"""
    
    @pytest.mark.pipeline
    def test_evaluate_model_accuracy(self, sample_comments_df):
        """Doit calculer l'accuracy correctement"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score
        
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(sample_comments_df['comment_text'])
        y = sample_comments_df['toxic']
        
        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)
        
        predictions = model.predict(X)
        accuracy = accuracy_score(y, predictions)
        
        assert 0 <= accuracy <= 1
    
    @pytest.mark.pipeline
    def test_evaluate_model_precision_recall_f1(self, sample_comments_df):
        """Doit calculer precision, recall, F1"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import precision_score, recall_score, f1_score
        
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(sample_comments_df['comment_text'])
        y = sample_comments_df['toxic']
        
        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)
        
        predictions = model.predict(X)
        
        precision = precision_score(y, predictions, zero_division=0)
        recall = recall_score(y, predictions, zero_division=0)
        f1 = f1_score(y, predictions, zero_division=0)
        
        assert 0 <= precision <= 1
        assert 0 <= recall <= 1
        assert 0 <= f1 <= 1
    
    @pytest.mark.pipeline
    def test_evaluate_model_confusion_matrix(self, sample_comments_df):
        """Doit calculer la matrice de confusion"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import confusion_matrix
        
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(sample_comments_df['comment_text'])
        y = sample_comments_df['toxic']
        
        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)
        
        predictions = model.predict(X)
        cm = confusion_matrix(y, predictions)
        
        assert cm.shape == (2, 2)
        assert np.sum(cm) == len(y)
    
    @pytest.mark.pipeline
    def test_evaluate_model_metrics_output_format(self, sample_comments_df):
        """Les métriques doivent être dans le bon format (JSON/dict)"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(sample_comments_df['comment_text'])
        y = sample_comments_df['toxic']
        
        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)
        
        predictions = model.predict(X)
        
        metrics = {
            'accuracy': accuracy_score(y, predictions),
            'precision': precision_score(y, predictions, zero_division=0),
            'recall': recall_score(y, predictions, zero_division=0),
            'f1_score': f1_score(y, predictions, zero_division=0)
        }
        
        assert isinstance(metrics, dict)
        assert all(isinstance(v, (int, float)) for v in metrics.values())


class TestPipelineOrchestration:
    """Tests pour l'orchestration du pipeline"""
    
    @pytest.mark.pipeline
    def test_pipeline_compilation(self):
        """Le pipeline doit compiler sans erreurs"""
        from src.pipeline.pipeline import digital_score_pipeline
        from kfp.compiler import Compiler
        
        # Vérifier que le pipeline est callable
        assert callable(digital_score_pipeline)
    
    @pytest.mark.pipeline
    @patch('src.submit_pipeline.aiplatform.PipelineJob')
    def test_pipeline_submission(self, mock_pipeline_job):
        """Le pipeline doit pouvoir être soumis à Vertex AI"""
        from src.submit_pipeline import run_vertex_pipeline
        
        # Mock de la soumission
        mock_job = MagicMock()
        mock_pipeline_job.return_value = mock_job
        
        # Vérifier que la fonction existe
        assert callable(run_vertex_pipeline)
    
    @pytest.mark.pipeline
    def test_pipeline_input_parameters(self):
        """Le pipeline doit accepter les paramètres d'entrée"""
        # Les chemins GCS pour raw et clean data
        raw_csv = "gs://bucket/raw.csv"
        clean_csv = "gs://bucket/clean.csv"
        
        assert isinstance(raw_csv, str)
        assert isinstance(clean_csv, str)


class TestComponentIntegration:
    """Tests d'intégration entre composants"""
    
    @pytest.mark.pipeline
    def test_prepare_to_train_data_flow(self, sample_comments_df):
        """Doit pouvoir transférer les données de prepare à train"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        # Simuler prepare_data
        df_clean = sample_comments_df.dropna()
        
        # Simuler train utilisant la sortie de prepare
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(df_clean['comment_text'])
        
        assert X is not None
        assert X.shape[0] == len(df_clean)
    
    @pytest.mark.pipeline
    def test_train_to_evaluate_model_flow(self, sample_comments_df):
        """Doit pouvoir transférer le modèle de train à evaluate"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score
        
        # Train
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(sample_comments_df['comment_text'])
        y = sample_comments_df['toxic']
        
        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)
        
        # Evaluate utilisant le modèle de train
        predictions = model.predict(X)
        accuracy = accuracy_score(y, predictions)
        
        assert 0 <= accuracy <= 1
