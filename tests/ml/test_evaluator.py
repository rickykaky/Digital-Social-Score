"""
Tests pour les métriques d'évaluation ML
Fichier: tests/ml/test_evaluator.py
"""

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score)


class TestMetricsCalculation:
    """Tests pour le calcul des métriques"""

    @pytest.mark.ml
    def test_accuracy_calculation(self):
        """Doit calculer l'accuracy correctement"""
        y_true = np.array([0, 1, 1, 0, 1, 0])
        y_pred = np.array([0, 1, 1, 0, 0, 0])

        accuracy = accuracy_score(y_true, y_pred)

        # 5 correctes sur 6
        expected = 5 / 6
        assert np.isclose(accuracy, expected)

    @pytest.mark.ml
    def test_precision_recall_f1(self):
        """Doit calculer precision, recall et F1 correctement"""
        y_true = np.array([0, 1, 1, 0, 1, 0])
        y_pred = np.array([0, 1, 1, 0, 0, 0])

        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)

        # TP=2, FP=0, FN=1, TN=3
        # Precision = TP / (TP + FP) = 2/2 = 1.0
        # Recall = TP / (TP + FN) = 2/3 = 0.667
        # F1 = 2 * (precision * recall) / (precision + recall) = 0.8

        assert precision == 1.0
        assert np.isclose(recall, 2 / 3)
        assert np.isclose(f1, 0.8)

    @pytest.mark.ml
    def test_confusion_matrix_calculation(self):
        """Doit calculer la matrice de confusion"""
        y_true = np.array([0, 1, 1, 0, 1, 0])
        y_pred = np.array([0, 1, 1, 0, 0, 0])

        cm = confusion_matrix(y_true, y_pred)

        # [[TN, FP],
        #  [FN, TP]]
        # [[3, 0],
        #  [1, 2]]
        expected = np.array([[3, 0], [1, 2]])
        assert np.array_equal(cm, expected)

    @pytest.mark.ml
    def test_roc_auc_calculation(self):
        """Doit calculer ROC-AUC"""
        y_true = np.array([0, 1, 1, 0, 1, 0])
        y_scores = np.array([0.1, 0.9, 0.8, 0.2, 0.7, 0.3])

        auc = roc_auc_score(y_true, y_scores)

        assert 0 <= auc <= 1
        # Pour ce cas, AUC devrait être 1.0 (parfait)
        assert np.isclose(auc, 1.0)


class TestEdgeCasesMetrics:
    """Tests pour les cas limites des métriques"""

    @pytest.mark.ml
    def test_all_correct_predictions(self):
        """Toutes les prédictions correctes = accuracy 1.0"""
        y_true = np.array([0, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 1])

        accuracy = accuracy_score(y_true, y_pred)
        assert accuracy == 1.0

    @pytest.mark.ml
    def test_all_wrong_predictions(self):
        """Toutes les prédictions erronées = accuracy 0.0"""
        y_true = np.array([0, 1, 0, 1])
        y_pred = np.array([1, 0, 1, 0])

        accuracy = accuracy_score(y_true, y_pred)
        assert accuracy == 0.0

    @pytest.mark.ml
    def test_all_same_class_true(self):
        """Si toutes les étiquettes réelles sont 1"""
        y_true = np.array([1, 1, 1, 1])
        y_pred = np.array([1, 1, 0, 1])

        recall = recall_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred)

        # TP=3, FN=1
        assert np.isclose(recall, 3 / 4)
        # TP=3, FP=0
        assert precision == 1.0

    @pytest.mark.ml
    def test_zero_division_precision(self):
        """Cas où FP=0 et TP=0 (pas de prédictions positives)"""
        y_true = np.array([0, 0, 1, 0])
        y_pred = np.array([0, 0, 0, 0])

        # zero_division=0 évite l'erreur
        precision = precision_score(y_true, y_pred, zero_division=0)
        assert precision == 0

    @pytest.mark.ml
    def test_imbalanced_classes(self):
        """Cas où les classes sont très déséquilibrées"""
        y_true = np.array([0] * 95 + [1] * 5)
        y_pred = np.array([0] * 97 + [1] * 3)

        accuracy = accuracy_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)

        # L'accuracy est trompeuse avec des données déséquilibrées
        assert accuracy > 0.9  # Élevé
        # F1 sera plus bas
        assert f1 < accuracy


class TestMetricsAggregate:
    """Tests pour l'agrégation de métriques"""

    @pytest.mark.ml
    def test_classification_report(self):
        """Doit produire un rapport de classification valide"""
        y_true = np.array([0, 1, 1, 0, 1, 0])
        y_pred = np.array([0, 1, 1, 0, 0, 0])

        report = classification_report(y_true, y_pred, output_dict=True)

        assert "precision" in report[0]
        assert "recall" in report[0]
        assert "f1-score" in report[0]
        assert "support" in report[0]

    @pytest.mark.ml
    def test_metrics_consistency(self):
        """Toutes les métriques doivent être cohérentes"""
        y_true = np.array([0, 1, 1, 0, 1, 0])
        y_pred = np.array([0, 1, 1, 0, 0, 0])

        metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred),
            "recall": recall_score(y_true, y_pred),
            "f1": f1_score(y_true, y_pred),
        }

        # Vérifier que toutes les métriques sont entre 0 et 1
        for metric, value in metrics.items():
            assert 0 <= value <= 1, f"{metric} = {value} not in [0, 1]"


class TestMetricsForBinaryClassification:
    """Tests spécifiques pour la classification binaire"""

    @pytest.mark.ml
    def test_binary_classification_metrics(self):
        """Toutes les métriques doivent être disponibles"""
        y_true = np.array([0, 1, 1, 0, 1, 0, 1, 1])
        y_pred = np.array([0, 1, 1, 0, 1, 0, 0, 1])

        metrics = {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision_0": precision_score(y_true, y_pred, pos_label=0),
            "precision_1": precision_score(y_true, y_pred, pos_label=1),
            "recall_0": recall_score(y_true, y_pred, pos_label=0),
            "recall_1": recall_score(y_true, y_pred, pos_label=1),
            "f1_macro": f1_score(y_true, y_pred, average="macro"),
            "f1_weighted": f1_score(y_true, y_pred, average="weighted"),
        }

        assert all(0 <= v <= 1 for v in metrics.values())

    @pytest.mark.ml
    def test_macro_vs_weighted_f1(self):
        """F1 macro vs weighted pour données déséquilibrées"""
        y_true = np.array([0] * 90 + [1] * 10)
        y_pred = np.array([0] * 85 + [1] * 5 + [1] * 10)

        f1_macro = f1_score(y_true, y_pred, average="macro")
        f1_weighted = f1_score(y_true, y_pred, average="weighted")

        # Weighted F1 doit être plus proche de macro quand données déséquilibrées
        assert isinstance(f1_macro, (int, float, np.number))
        assert isinstance(f1_weighted, (int, float, np.number))


class TestMetricsForProbabilities:
    """Tests pour les métriques basées sur les probabilités"""

    @pytest.mark.ml
    def test_roc_auc_with_probabilities(self):
        """ROC-AUC doit fonctionner avec des probabilités"""
        y_true = np.array([0, 1, 1, 0, 1, 0])
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7, 0.3])

        auc = roc_auc_score(y_true, y_proba)

        assert 0 <= auc <= 1

    @pytest.mark.ml
    def test_roc_auc_extreme_cases(self):
        """ROC-AUC pour cas extrêmes"""
        # Parfait
        y_true = np.array([0, 0, 1, 1])
        y_proba = np.array([0.1, 0.2, 0.8, 0.9])
        auc_perfect = roc_auc_score(y_true, y_proba)
        assert np.isclose(auc_perfect, 1.0)

        # Horrible
        y_proba = np.array([0.9, 0.8, 0.2, 0.1])
        auc_terrible = roc_auc_score(y_true, y_proba)
        assert np.isclose(auc_terrible, 0.0)


class TestMetricsAggregation:
    """Tests pour l'agrégation de résultats"""

    @pytest.mark.ml
    def test_multiple_models_metrics(self):
        """Comparer les métriques de plusieurs modèles"""
        y_true = np.array([0, 1, 1, 0, 1, 0, 1, 1, 0, 0])

        # Model 1
        y_pred_1 = np.array([0, 1, 1, 0, 1, 0, 1, 1, 0, 0])

        # Model 2
        y_pred_2 = np.array([0, 1, 0, 0, 1, 0, 1, 0, 0, 0])

        metrics_1 = {
            "accuracy": accuracy_score(y_true, y_pred_1),
            "f1": f1_score(y_true, y_pred_1),
        }

        metrics_2 = {
            "accuracy": accuracy_score(y_true, y_pred_2),
            "f1": f1_score(y_true, y_pred_2),
        }

        # Model 1 devrait être meilleur
        assert metrics_1["accuracy"] > metrics_2["accuracy"]

    @pytest.mark.ml
    def test_metrics_dataframe_format(self):
        """Les métriques devraient pouvoir être dans un DataFrame"""
        y_true = np.array([0, 1, 1, 0, 1, 0])
        y_pred = np.array([0, 1, 1, 0, 0, 0])

        metrics = pd.DataFrame(
            {
                "model": ["Model A"],
                "accuracy": [accuracy_score(y_true, y_pred)],
                "precision": [precision_score(y_true, y_pred)],
                "recall": [recall_score(y_true, y_pred)],
                "f1": [f1_score(y_true, y_pred)],
            }
        )

        assert isinstance(metrics, pd.DataFrame)
        assert len(metrics) == 1
        assert all(
            col in metrics.columns
            for col in ["model", "accuracy", "precision", "recall", "f1"]
        )
