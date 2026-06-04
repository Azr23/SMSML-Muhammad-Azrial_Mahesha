import os
import time
import json
import logging
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Email Phishing Detection API", version="1.0")

# Setup logging to a file for the Prometheus exporter to read
LOG_FILE = os.path.join(os.path.dirname(__file__), "predictions.log")
logger = logging.getLogger("prediction_logger")
logger.setLevel(logging.INFO)
# Avoid duplicate handlers if app is reloaded
if not logger.handlers:
    file_handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# Load the model
MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "Membangun_model",
    "mlruns",
    "121754710912968073",
    "models",
    "m-34db24d788bc45188f5d4bb27107088c",
    "artifacts",
    "model.pkl"
)

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")

try:
    model = joblib.load(MODEL_PATH)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    raise e

class PredictionInput(BaseModel):
    sender_email_clean: str
    subject_clean: str
    sender_domain: str
    has_link: int
    has_attachment: int
    urgency_score: int
    spelling_errors: int
    email_length_words: int
    subject_word_count: int

@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict")
def predict(data: PredictionInput):
    start_time = time.time()
    try:
        # Prepare input data as a pandas DataFrame
        input_dict = {
            "sender_email_clean": [data.sender_email_clean],
            "subject_clean": [data.subject_clean],
            "sender_domain": [data.sender_domain],
            "has_link": [data.has_link],
            "has_attachment": [data.has_attachment],
            "urgency_score": [data.urgency_score],
            "spelling_errors": [data.spelling_errors],
            "email_length_words": [data.email_length_words],
            "subject_word_count": [data.subject_word_count]
        }
        df = pd.DataFrame(input_dict)
        
        # Run prediction
        prediction = int(model.predict(df)[0])
        probabilities = model.predict_proba(df)[0]
        phishing_probability = float(probabilities[1])
        
        latency = time.time() - start_time
        
        prediction_label = "phishing" if prediction == 1 else "legitimate"
        
        # Prepare log entry
        log_entry = {
            "timestamp": time.time(),
            "prediction": prediction_label,
            "probability": phishing_probability,
            "latency": latency,
            "email_length_words": data.email_length_words,
            "status": "success"
        }
        
        # Log prediction to file for exporter
        logger.info(json.dumps(log_entry))
        
        return {
            "prediction": prediction,
            "label": prediction_label,
            "probability": phishing_probability,
            "latency_seconds": latency
        }
    except Exception as e:
        latency = time.time() - start_time
        log_entry = {
            "timestamp": time.time(),
            "prediction": "unknown",
            "probability": 0.0,
            "latency": latency,
            "email_length_words": 0,
            "status": "error",
            "error_msg": str(e)
        }
        logger.info(json.dumps(log_entry))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
