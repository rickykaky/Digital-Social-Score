"""
Script de soumission du pipeline Kubeflow à Vertex AI Pipelines
Exécute le pipeline compilé sur Google Cloud Vertex AI
"""

from google.cloud import aiplatform
import os
import sys
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_vertex_pipeline(
    project_id: str = None,
    region: str = "us-central1",
    pipeline_name: str = "digital-social-score-pipeline",
    template_path: str = None,
    pipeline_root: str = None,
    bucket_name: str = None
):
    """
    Soumet le pipeline Kubeflow compilé à Vertex AI Pipelines.
    
    Args:
        project_id: ID du projet GCP (détecté automatiquement si None)
        region: Région GCP pour l'exécution du pipeline
        pipeline_name: Nom d'affichage du pipeline
        template_path: Chemin vers le fichier YAML du pipeline compilé
        pipeline_root: Chemin GCS pour stocker les artefacts du pipeline
        bucket_name: Nom du bucket GCS pour stocker les fichiers
    """
    
    # Détection automatique du projet GCP
    if project_id is None:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT_ID")
        if not project_id:
            logger.error("❌ Impossible de déterminer le projet GCP. Définissez GOOGLE_CLOUD_PROJECT ou GCP_PROJECT_ID")
            sys.exit(1)
    
    # Définition des chemins par défaut
    if bucket_name is None:
        bucket_name = f"{project_id}-digital-social-score"
    
    if template_path is None:
        template_path = f"gs://{bucket_name}/pipeline-templates/digital_score_pipeline.yaml"
    
    if pipeline_root is None:
        pipeline_root = f"gs://{bucket_name}/pipeline-root"
    
    logger.info(f"📋 Configuration du Pipeline Vertex AI")
    logger.info(f"  Projet: {project_id}")
    logger.info(f"  Région: {region}")
    logger.info(f"  Template: {template_path}")
    logger.info(f"  Pipeline Root: {pipeline_root}")
    
    try:
        # Initialisation de Vertex AI
        logger.info(f"🔐 Initialisation de Vertex AI...")
        aiplatform.init(
            project=project_id,
            location=region,
        )
        
        # Lecture du fichier YAML compilé
        logger.info(f"📄 Chargement du template du pipeline...")
        with open(template_path, 'r') as f:
            pipeline_definition = f.read()
        
        # Création du job pipeline
        logger.info(f"🚀 Création du job pipeline...")
        pipeline_job = aiplatform.PipelineJob(
            display_name=pipeline_name,
            template_path=template_path,
            pipeline_root=pipeline_root,
            # Paramètres du pipeline (si nécessaire)
            parameter_values={
                "raw_csv_path": f"gs://{bucket_name}/data/train.csv",
                "clean_csv_path": f"gs://{bucket_name}/data/clean.csv"
            },
            location=region,
        )
        
        # Soumission du pipeline
        logger.info(f"📤 Soumission du pipeline...")
        pipeline_job.submit(
            service_account=f"vertex-ai-sa@{project_id}.iam.gserviceaccount.com"
        )
        
        logger.info(f"✅ Pipeline soumis avec succès !")
        logger.info(f"   Nom du job: {pipeline_job.display_name}")
        logger.info(f"   Resource Name: {pipeline_job.resource_name}")
        logger.info(f"   URL: https://console.cloud.google.com/vertex-ai/pipelines/runs?project={project_id}")
        
        return pipeline_job
        
    except FileNotFoundError:
        logger.error(f"❌ Fichier template non trouvé: {template_path}")
        logger.error(f"   Assurez-vous que le fichier existe et est accessible")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"❌ Erreur lors de la soumission du pipeline: {e}")
        sys.exit(1)


def submit_pipeline_from_local(
    project_id: str = None,
    region: str = "us-central1",
    pipeline_name: str = "digital-social-score-pipeline",
    local_template_path: str = "./digital_score_pipeline.yaml",
    bucket_name: str = None
):
    """
    Compile le pipeline localement et le soumet à Vertex AI.
    À utiliser quand le fichier YAML n'est pas encore compilé.
    """
    
    if project_id is None:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT_ID")
        if not project_id:
            logger.error("❌ Impossible de déterminer le projet GCP")
            sys.exit(1)
    
    if bucket_name is None:
        bucket_name = f"{project_id}-digital-social-score"
    
    pipeline_root = f"gs://{bucket_name}/pipeline-root"
    
    logger.info(f"🔨 Compilation du pipeline...")
    try:
        from kfp.v2 import compiler
        from src.pipeline.pipeline import digital_score_pipeline
        
        # Compiler le pipeline
        compiler.Compiler().compile(
            pipeline_func=digital_score_pipeline,
            package_path=local_template_path
        )
        logger.info(f"✓ Pipeline compilé: {local_template_path}")
        
    except ImportError as e:
        logger.error(f"❌ Impossible d'importer KFP: {e}")
        logger.error(f"   Installez KFP avec: pip install kfp==2.0.0")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"❌ Erreur lors de la compilation: {e}")
        sys.exit(1)
    
    # Soumettre le pipeline compilé
    template_path = f"gs://{bucket_name}/pipeline-templates/{local_template_path}"
    return run_vertex_pipeline(
        project_id=project_id,
        region=region,
        pipeline_name=pipeline_name,
        template_path=template_path,
        pipeline_root=pipeline_root,
        bucket_name=bucket_name
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Soumet le pipeline Digital Social Score à Vertex AI Pipelines"
    )
    parser.add_argument("--project", help="ID du projet GCP", default=None)
    parser.add_argument("--region", help="Région GCP", default="us-central1")
    parser.add_argument("--name", help="Nom du pipeline", default="digital-social-score-pipeline")
    parser.add_argument("--template", help="Chemin du template YAML compilé", default=None)
    parser.add_argument("--root", help="Chemin du pipeline root (GCS)", default=None)
    parser.add_argument("--bucket", help="Nom du bucket GCS", default=None)
    parser.add_argument("--compile", action="store_true", help="Compiler le pipeline avant soumission")
    
    args = parser.parse_args()
    
    if args.compile:
        logger.info("Mode compilation + soumission activé")
        submit_pipeline_from_local(
            project_id=args.project,
            region=args.region,
            pipeline_name=args.name,
            bucket_name=args.bucket
        )
    else:
        logger.info("Mode soumission uniquement")
        run_vertex_pipeline(
            project_id=args.project,
            region=args.region,
            pipeline_name=args.name,
            template_path=args.template,
            pipeline_root=args.root,
            bucket_name=args.bucket
        )
