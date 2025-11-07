# ...existing code...
from kfp.v2 import dsl
from kfp.v2.dsl import component, Input, Output, Model, Artifact

@component(packages_to_install=["pandas"])
def prepare_data_op(raw_csv_path: str, clean_csv: Output[Artifact]):
    """Read raw CSV, do simple cleaning, write cleaned CSV to clean_csv.path"""
    import pandas as pd
    df = pd.read_csv(raw_csv_path)
    # simple cleaning example (adapt)
    df.dropna(subset=["comment_text"], inplace=True)
    df.to_csv(clean_csv.path, index=False)

@component(packages_to_install=["pandas", "scikit-learn", "joblib"])
def train_model_op(clean_csv: Input[Artifact], model: Output[Model]):
    """Train a placeholder model and save it to model.path"""
    import pandas as pd
    from sklearn.dummy import DummyClassifier
    import joblib

    df = pd.read_csv(clean_csv.path)
    X = df["comment_text"].astype(str)  # placeholder: you should vectorize
    y = df[["toxic","severe_toxic","obscene","threat","insult","identity_hate"]].iloc[:,0]  # example for single-label demo

    # Placeholder training (replace with real vectorizer + model)
    clf = DummyClassifier(strategy="most_frequent")
    clf.fit([[0]] * len(y), y)  # dummy fit; replace with real features
    joblib.dump(clf, model.path)

@component(packages_to_install=["pandas", "joblib", "scikit-learn"])
def evaluate_model_op(model: Input[Model], data: Input[Artifact]) -> float:
    """Load model and compute a dummy score (replace with real evaluation)"""
    import joblib, pandas as pd
    df = pd.read_csv(data.path)
    clf = joblib.load(model.path)
    # dummy score
    score = 0.0
    return float(score)

@dsl.pipeline(name="example-pipeline", pipeline_root="gs://my-bucket/pipeline-root")
def pipeline(raw_csv: str = "gs://my-bucket/data/raw.csv"):
    # prepare
    prepare_task = prepare_data_op(raw_csv_path=raw_csv)
    # train (use the clean_csv output produced by prepare_data_op)
    train_task = train_model_op(clean_csv=prepare_task.outputs["clean_csv"])
    # evaluate (use the trained model and the cleaned data)
    eval_task = evaluate_model_op(model=train_task.outputs["model"], data=prepare_task.outputs["clean_csv"])
    # expose pipeline output (optional)
    dsl.get_pipeline_conf().add_op_transformer(lambda op: op)  # placeholder
# ...existing code...