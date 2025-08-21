import sys, os
import pandas as pd
import certifi
ca = certifi.where()

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
from uvicorn import run as app_run

from dotenv import load_dotenv
import pymongo

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.constant.training_pipeline import (
    DATA_INGESTION_COLLECTION_NAME,
    DATA_INGESTION_DATABASE_NAME,
)

from fastapi.templating import Jinja2Templates

## configuration of fastapi
app = FastAPI(
    title="Network Security API",
    description="API for training and prediction",
    version="1.0.0",
    servers=[
        {"url": "http://localhost:8000", "description": "Local server"},
        {"url": "https://your-deployed-url.com", "description": "Production server"}
    ]
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


load_dotenv()
mongo_db_url = os.getenv("MONGODB_URL_KEY")
print(f"MongoDB URL: {mongo_db_url}")

client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]


templates = Jinja2Templates(directory="./templates")



try:
    preprocessor = load_object("final_model/preprocessor.pkl")
    final_model = load_object("final_model/model.pkl")
    network_model = NetworkModel(preprocessor=preprocessor, model=final_model)
    print("✅ Model and preprocessor loaded successfully at startup.")
except Exception as e:
    print("❌ Failed to load model/preprocessor at startup:", e)
    network_model = None


@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")


@app.get("/train", tags=["train"])
async def train_route():
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response(content="Training is successful", media_type="text/plain")
    except Exception as e:
        import traceback
        error_message = f"Training Failed: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_message)
        return Response(content=error_message, status_code=500, media_type="text/plain")
    


@app.post("/predict")
async def predict_route(request: Request, file: UploadFile = File(...)):
    try:
        if network_model is None:
            return Response(content="Model not loaded!", status_code=500)

        df = pd.read_csv(file.file)

        y_pred = network_model.predict(df)
        df["predicted_column"] = y_pred

        #save predictions to CSV
        os.makedirs("prediction_output", exist_ok=True)
        output_path = "prediction_output/output.csv"
        df.to_csv(output_path, index=False)

        ## generates HTML table
        table_html = df.to_html(classes="table table-striped", index=False)
        return templates.TemplateResponse(
            "table.html", {"request": request, "table": table_html}
        )

    except Exception as e:
        raise NetworkSecurityException(e, sys)


if __name__ == "__main__":
    app_run(app, host="localhost", port=8080)
