from google.cloud import aiplatform
def run_vertex_pipeline():
 # Initialisation de Vertex AI
 aiplatform.init(
 project="digital-social-score",
 location="europe-west1-a", # Exemple, adaptez selon région
 )
 # Création de la définition du job pipeline
 pipeline_job = aiplatform.PipelineJob(
 display_name="pipeline-DSS",
 template_path="gs://bucket/pipeline-definition.json", # chemin du pipeline compilé
 pipeline_root="gs://bucket/pipeline-root/",
 parameter_values={ # liste des paramètres si nécessaires
 "param1": "valeur1",
 # ajouter d'autres paramètres selon besoin
 },
 )
 # Soumission du job pipeline qui lance l'exécution
 pipeline_job.submit()
 print("Pipeline Vertex AI déclenché avec succès.")
if __name__ == "__main__":
  
 run_vertex_pipeline()