"""
Submit Vertex Pipeline (Asynchrone) - Soumet le pipeline sans bloquer Cloud Build
Ce fichier implémente la désynchronisation des pipelines pour ne pas bloquer le déploiement
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from google.cloud import aiplatform

# Configuration logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def submit_vertex_pipeline_async(
    project_id: str,
    region: str = "us-west1",
    pipeline_yaml: str = "digital_score_pipeline.yaml",
    display_name: str = "Digital-Social-Score-Pipeline",
    pipeline_root: str = "gs://digital-social-score/pipeline-root",
    async_mode: bool = True,
    wait_timeout: Optional[int] = None,
) -> str:
    """
    Soumet le pipeline à Vertex AI Pipelines.

    Si async_mode=True: Soumet et retourne immédiatement (non bloquant)
    Si async_mode=False et wait_timeout: Attend la fin du pipeline

    Args:
        project_id: Google Cloud Project ID
        region: Région GCP (ex: europe-west1)
        pipeline_yaml: Chemin du fichier YAML compilé
        display_name: Nom d'affichage du pipeline
        pipeline_root: Bucket GCS pour les artifacts
        async_mode: Si True, retour immédiat (asynchrone)
        wait_timeout: Timeout en secondes si async_mode=False

    Returns:
        Job name du pipeline soumis
    """

    logger.info(f"🚀 Initialisation de Vertex AI Pipelines")
    logger.info(f"   Projet: {project_id}")
    logger.info(f"   Région: {region}")
    logger.info(f"   Mode: {'ASYNCHRONE ⚡' if async_mode else 'SYNCHRONE ⏳'}")

    # Initialisation de Vertex AI
    aiplatform.init(project=project_id, location=region)

    # Vérifier le fichier YAML
    yaml_path = Path(pipeline_yaml)
    if not yaml_path.exists():
        logger.error(f"❌ Fichier pipeline YAML non trouvé: {pipeline_yaml}")
        raise FileNotFoundError(f"Fichier non trouvé: {pipeline_yaml}")

    logger.info(f"✅ Fichier pipeline trouvé: {pipeline_yaml}")

    # Créer le job pipeline
    logger.info(f"📝 Création du job pipeline: {display_name}")
    try:
        pipeline_job = aiplatform.PipelineJob(
            display_name=display_name,
            template_path=str(yaml_path),
            pipeline_root=pipeline_root,
            parameter_values={
                "raw_csv_path": "gs://digital-social-score/data/train.csv",
                "clean_csv_path": "gs://digital-social-score/data/clean.csv",
            },
        )
        logger.info(f"✅ Job pipeline créé")
    except Exception as e:
        logger.error(f"❌ Erreur création du job: {e}", exc_info=True)
        raise

    # Soumettre le pipeline
    logger.info(f"🔄 Soumission du pipeline à Vertex AI...")
    try:
        pipeline_job.submit()
        logger.info(f"✅ Pipeline soumis avec succès!")
        logger.info(f"   Job ID: {pipeline_job.name}")
        logger.info(f"   Job Resource Name: {pipeline_job.resource_name}")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la soumission: {e}", exc_info=True)
        raise

    # Mode asynchrone: Retour immédiat sans attendre
    if async_mode:
        logger.info(f"⚡ Mode ASYNCHRONE activé - Retour immédiat")
        logger.info(f"📊 Consultez l'état du pipeline sur:")
        logger.info(
            f"   https://console.cloud.google.com/vertex-ai/pipelines/runs/{pipeline_job.resource_name.split('/')[-1]}"
        )
        logger.info(f"💡 L'entraînement du modèle s'exécute en arrière-plan")
        logger.info(f"💡 Le déploiement GKE continue indépendamment")
        return pipeline_job.name

    # Mode synchrone: Attendre la fin du pipeline
    else:
        logger.info(f"⏳ Mode SYNCHRONE activé - Attente de la fin du pipeline...")
        logger.info(
            f"⏱️  Timeout: {wait_timeout}s" if wait_timeout else "⏱️  Pas de timeout"
        )

        try:
            # Attendre la fin du pipeline
            pipeline_job.wait(timeout=wait_timeout)
            logger.info(f"✅ Pipeline terminé avec succès!")
            logger.info(f"   État: {pipeline_job.state}")

            return pipeline_job.name

        except TimeoutError:
            logger.warning(f"⚠️  Timeout atteint ({wait_timeout}s)")
            logger.warning(f"   Le pipeline continue en arrière-plan")
            logger.info(f"📊 Consultez l'état du pipeline sur:")
            logger.info(
                f"   https://console.cloud.google.com/vertex-ai/pipelines/runs/{pipeline_job.resource_name.split('/')[-1]}"
            )
            return pipeline_job.name

        except Exception as e:
            logger.error(f"❌ Erreur lors de l'attente: {e}", exc_info=True)
            logger.warning(f"   Le pipeline continue en arrière-plan")
            return pipeline_job.name


def main():
    """Point d'entrée principal."""

    parser = argparse.ArgumentParser(
        description="Soumet le pipeline Digital Social Score à Vertex AI Pipelines (ASYNCHRONE par défaut)"
    )

    parser.add_argument("--project", required=True, help="Google Cloud Project ID")
    parser.add_argument(
        "--region", default="europe-west1", help="GCP Region (défaut: europe-west1)"
    )
    parser.add_argument(
        "--yaml",
        default="digital_score_pipeline.yaml",
        help="Chemin du fichier YAML compilé (défaut: digital_score_pipeline.yaml)",
    )
    parser.add_argument(
        "--display-name",
        default="Digital-Social-Score-Pipeline",
        help="Nom du pipeline",
    )
    parser.add_argument(
        "--pipeline-root",
        default="gs://digital-social-score/pipeline-root",
        help="Bucket GCS pour les artifacts",
    )
    parser.add_argument(
        "--async",
        action="store_true",
        default=True,
        help="Mode asynchrone: soumet et retourne immédiatement (défaut: True)",
    )
    parser.add_argument(
        "--sync", action="store_true", help="Mode synchrone: attend la fin du pipeline"
    )
    parser.add_argument(
        "--wait-timeout",
        type=int,
        default=None,
        help="Timeout en secondes en mode synchrone (défaut: None)",
    )

    args = parser.parse_args()

    # Déterminer le mode
    async_mode = not args.sync

    try:
        job_name = submit_vertex_pipeline_async(
            project_id=args.project,
            region=args.region,
            pipeline_yaml=args.yaml,
            display_name=args.display_name,
            pipeline_root=args.pipeline_root,
            async_mode=async_mode,
            wait_timeout=args.wait_timeout if args.sync else None,
        )

        logger.info(f"✅ Pipeline lancé avec succès!")
        logger.info(f"   Job: {job_name}")
        return 0

    except Exception as e:
        logger.error(f"❌ Erreur: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
