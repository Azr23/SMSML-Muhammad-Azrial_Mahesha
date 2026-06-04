import os
import time
import json
from prometheus_client import start_http_server, Counter, Histogram

# Expose port 8001 for metrics scraping
METRICS_PORT = 8001
LOG_FILE = os.path.join(os.path.dirname(__file__), "predictions.log")

# Setup Prometheus metrics
API_REQUESTS_TOTAL = Counter(
    "ml_api_requests_total", 
    "Total requests served", 
    ["status"]
)
PREDICTION_DURATION_SECONDS = Histogram(
    "ml_prediction_duration_seconds", 
    "Prediction latency distribution in seconds",
    buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)
PREDICTIONS_TOTAL = Counter(
    "ml_predictions_total", 
    "Prediction labels count", 
    ["label"]
)
PREDICTION_PROBABILITIES = Histogram(
    "ml_prediction_probabilities", 
    "Model output probabilities", 
    buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)
EMAIL_LENGTH_WORDS = Histogram(
    "ml_email_length_words", 
    "Distribution of email lengths in words", 
    buckets=[0, 10, 25, 50, 75, 100, 150, 200, 250, 300, 500, 1000]
)

def process_log_line(line):
    """Parse a single JSON log line and update Prometheus metrics."""
    try:
        data = json.loads(line.strip())
        status = data.get("status", "success")
        
        # 1. Update API requests total
        API_REQUESTS_TOTAL.labels(status=status).inc()
        
        # 2. Update prediction latency
        latency = data.get("latency", 0.0)
        PREDICTION_DURATION_SECONDS.observe(latency)
        
        if status == "success":
            # 3. Update predictions count
            label = data.get("prediction", "unknown")
            PREDICTIONS_TOTAL.labels(label=label).inc()
            
            # 4. Update prediction probabilities
            prob = data.get("probability", 0.0)
            PREDICTION_PROBABILITIES.observe(prob)
            
            # 5. Update email length
            words = data.get("email_length_words", 0)
            EMAIL_LENGTH_WORDS.observe(words)
            
    except Exception as e:
        print(f"Error parsing log line: {e}")

def main():
    print(f"Starting Prometheus Exporter on port {METRICS_PORT}...")
    start_http_server(METRICS_PORT)
    
    # Initialize log file if it doesn't exist
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            pass
            
    # Read existing logs to catch up state on startup
    print("Reading existing log lines...")
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                process_log_line(line)
                
    print("Watching for new predictions in real-time...")
    # Tail the log file
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        # Move to the end of the file
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            process_log_line(line)

if __name__ == "__main__":
    main()
