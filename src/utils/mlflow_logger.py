import mlflow
import os

class MLFlowTracker:
    def __init__(self, experiment_name: str):
        # تنظیم ساده به دایرکتوری نسبی در پروژه
        # این کار از خطاهای Permission مربوط به مسیرهای مطلق جلوگیری می‌کند
        mlflow.set_tracking_uri("mlruns")
        mlflow.set_experiment(experiment_name)

    def log_run(self, params: dict, metrics: dict):
        with mlflow.start_run():
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            print("Successfully logged run.")

    def log_evaluation_with_artifact(self, params: dict, metrics: dict, model_path: str):
        with mlflow.start_run():
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            
            if os.path.exists(model_path):
                # کپی مدل به عنوان Artifact
                mlflow.log_artifact(model_path)
                print(f"Logged artifact: {model_path}")
            else:
                print(f"Warning: {model_path} not found.")
