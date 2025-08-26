Network Security — ML Pipeline for Threat/Phishing Detection

An end-to-end, production-minded ML pipeline that ingests network/phishing data, validates schema & drift, transforms with robust preprocessing, trains multiple classifiers with guardrails, tracks metrics via MLflow, and automatically syncs artifacts/models to AWS S3. The project is Dockerized and wired for CI/CD to push container images to Amazon ECR.

Overview:

-Goal: Train a classifier on phisingData.csv to predict the Result (target), producing reproducible artifacts + a final model. 
-Pipeline stages: Data Ingestion → Data Validation (incl. drift) → Data Transformation → Model Training → Cloud Sync (S3). 
-Operational posture: Docker + GitHub Actions to build/push to Amazon ECR; artifacts & models sync to S3 with timestamped lineage.


Key Features:

-Data Quality Gates: Schema checks, valid/invalid separation, and data-drift report using a KS test across columns. 
-Preprocessing: KNN imputation (n_neighbors=3) persisted as preprocessor.pkl for stable inference. 
-Model Training: Candidates include RandomForest, DecisionTree, GradientBoosting, LogisticRegression, and AdaBoost with basic hyper-parameter sweeps; best model persisted. 
-Guardrails: Expected accuracy ≥ 0.60 and generalization gap ≤ 0.05. 
-Experiment Tracking: Logs F1, precision, recall + model via MLflow. 
-Cloud Sync: Artifacts and final model auto-uploaded to S3 under timestamped paths. 
-API for Ops: FastAPI server exposes /train and /predict (CSV upload → HTML table + saved predictions).

Project structure:

Network-security/
├─ networksecurity/
│  ├─ components/               # ingestion, validation, transformation, training
│  ├─ pipeline/training_pipeline.py
│  ├─ cloud/s3_syncer.py
│  ├─ entity/, exception/, logging/, constant/
├─ data_schema/schema.yaml
├─ final_model/                 # persisted preprocessor/model
├─ saved_models/
├─ Artifacts/                   # timestamped run outputs
├─ app.py                       # FastAPI (train + predict)
├─ Dockerfile
├─ requirements.txt
└─ .github/workflows/workflow.yml

Data & Configuration:

-Target column: Result
-Dataset: phisingData.csv
-Split: 80/20 (test ratio = 0.2)
-Schema: data_schema/schema.yaml enforces expected columns/dtypes
-Imputation: KNN (n_neighbors=3)
-Thresholds: expected score ≥ 0.60; over/under-fit threshold ≤ 0.05
All above are encoded in constants/config & validation routines. 

MongoDB (optional source): Database SANHITH, collection NetworkData (ingestion can read from Mongo).

How the Pipeline Runs:

-Ingestion: Reads from file or MongoDB; writes feature-store copy; performs train/test split. 
-Validation: Verifies column counts; runs KS-test drift; writes drift_report.yaml; marks valid/invalid sets. 
-Transformation: Fits KNN imputer; persists preprocessor.pkl; writes transformed .npy arrays. 
-Training: Trains candidate models + basic param grids; computes metrics; tracks with MLflow; persists best model. 
-Sync: Uploads Artifacts/ and final_model/ to S3 (s3://sannynetworksecurity/.../<TIMESTAMP>). 

FastAPI Endpoints:

-GET /train — kicks off the full training pipeline and returns status. 
-POST /predict — upload a CSV; server returns an HTML table with predictions and saves prediction_output/output.-csv. 
-GET /upload — simple HTML form to post a CSV to /predict. 
-The API loads final_model/preprocessor.pkl and final_model/model.pkl on startup if available. 

Getting Started
Prerequisites

Python 3.10
(Optional) Docker
AWS CLI v2 configured with S3/ECR permissions (for sync & CI) 

Setup:

python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt


Environment & Secrets:

Create a .env with Mongo credentials (note the naming used across modules):
# used by Data Ingestion
MONGO_DB_URL=<your-mongodb-connection-string>
# used by FastAPI app to connect (align with the above!)
MONGODB_URL_KEY=<your-mongodb-connection-string>

The ingestion code expects MONGO_DB_URL, while the API uses MONGODB_URL_KEY; keep them consistent to avoid confusion. 

AWS: The constant TRAINING_BUCKET_NAME defaults to sannynetworksecurity. Change it (or parameterize) for your environment. 

-Run the API locally
python app.py
# Open http://localhost:8000/docs
# Trigger training via GET /train
# Upload a CSV to /predict (or use GET /upload for a simple form)

Docker
Build and run:

-docker build -t network-security:latest .
docker run --rm \
     -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
     -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
     -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
     -p 8000:8000 \
    network-security:latest

Base image: python:3.10-slim-bullseye. Pass AWS creds if you want S3 sync from inside the container. 

CI/CD (GitHub Actions → Amazon ECR):

On push to main, the workflow builds the Docker image and pushes to ECR.
-Set repository secrets:
-AWS_ACCESS_KEY_ID
-AWS_SECRET_ACCESS_KEY
-AWS_REGION
-ECR_REPOSITORY_NAME (e.g., network-security)

The workflow logs into ECR and publishes the image for downstream deployment (EC2/ECS). 

Cloud Sync (S3):

-After training, these paths are automatically synced:
-Artifacts/ → s3://sannynetworksecurity/Artifacts/<TIMESTAMP>
-final_model/ → s3://sannynetworksecurity/final_model/<TIMESTAMP>
-Handled by S3Sync.sync_folder_to_s3(...). 
-Configuration Reference (selected)

Central constants (paths, split ratios, thresholds, file names, etc.). 
Training models & param grids (RandomForest, DecisionTree, GradientBoosting, LogisticRegression, AdaBoost). 
MLflow metric logging in the trainer. 

Troubleshooting:

-S3 sync failures → verify AWS credentials/permissions and bucket name. 
-Drift report missing → ensure data_schema/schema.yaml exists and matches dataset columns. 
-ECR push fails → confirm repository name/region and that login occurs before push. 
-Docker apt issues → keep a slim base and clean apt lists. 

Roadmap:
-Add unit tests and wire into CI
-Add richer evaluation (confusion matrix, ROC-AUC) + model registry
-Parameterize S3 bucket & ECR repo via envs
-ECS/EC2 deployment pattern (ALB, autoscaling)
