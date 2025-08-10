#!/usr/bin/env python3
from logger import setup_logger
from metrics import collect_metrics, post_metrics
import os
import time


if __name__ == "__main__":
    logger = setup_logger()

    url = "http://localhost:8000/api/devices/"

    containerized = os.environ.get("CONTAINERIZED", "false").lower() == "true"

    logger.info(f"Containerized mode: {containerized}")
    
    if containerized:
        while True:
            metrics = collect_metrics()
            response = post_metrics(metrics, url)
    else:
        metrics = collect_metrics()
        response = post_metrics(metrics, url)





