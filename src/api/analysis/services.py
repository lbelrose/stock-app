import pandas as pd
import numpy as np
import yfinance as yf
import os
from .features import generate_technical_features

import json
import subprocess
import sys

from models.base_model import BaseModel
from models.model_factory import ModelFactory

class AnalysisService:
    _training_processes = {} # Track running training processes

    @classmethod
    def train_model_generic(cls, ticker: str, model_class_name: str, **model_kwargs) -> dict:
        """
        Triggers the training of a prediction model for a given stock ticker using the generic train_model script.
        """
        if ticker in cls._training_processes:
            proc = cls._training_processes[ticker]
            if proc.poll() is None: # Process is still running
                return {
                    "status": "training_in_progress",
                    "message": f"A specialist model for {ticker} is still being generated. Please try again in a moment."
                }
            else: # Process finished
                del cls._training_processes[ticker]
        
        print(f"Specialist model for {ticker} not found or training requested. Starting background training.")
        python_executable = sys.executable # Use the same python interpreter
        command = [
            python_executable,
            "-m", "analysis.train_model", # Call train_model as a module
            "--ticker", ticker,
            "--model_class", model_class_name
        ]
        for key, value in model_kwargs.items():
            command.extend([f"--{key}", str(value)])
        
        # Start the process in the background
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) # src/api
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=project_root)
        cls._training_processes[ticker] = proc

        return {
            "status": "training_started",
            "message": f"A specialist model for {ticker} is being generated. Please try again in a few minutes."
        }

    @classmethod
    def get_prediction_generic(cls, ticker: str) -> dict:
        """
        Provides a buy/sell/hold prediction for a given stock ticker using the generic prediction script.
        """
        python_executable = sys.executable
        command = [
            python_executable,
            "-m", "analysis.predict_next_day", # Call predict_next_day as a module
            "--ticker", ticker
        ]
        
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) # src/api
        try:
            result = subprocess.run(command, cwd=project_root, capture_output=True, text=True, check=True)
            # The predict_next_day script prints the JSON output, so we need to parse it
            output_lines = result.stdout.strip().split('\n')
            # Find the JSON part, which is usually the last part of the output
            json_output = "{}"
            for line in reversed(output_lines):
                if line.startswith('{') and line.endswith('}'):
                    json_output = line
                    break
            
            prediction_data = json.loads(json_output)
            return prediction_data
        except subprocess.CalledProcessError as e:
            print(f"Error running prediction for {ticker}: {e}")
            print(e.stdout)
            print(e.stderr)
            raise ValueError(f"Prediction failed for {ticker}: {e.stderr}")
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error for {ticker}: {e}")
            print(f"Raw stdout: {result.stdout}")
            raise ValueError(f"Failed to parse prediction output for {ticker}.")
        except FileNotFoundError:
            raise FileNotFoundError(f"Prediction script or model not found for {ticker}.")
        except Exception as e:
            print(f"An unexpected error occurred during prediction for {ticker}: {e}")
            raise
    