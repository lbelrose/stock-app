import os

import subprocess
import sys
from  .predict_next_day import predict_next_day 

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
        return predict_next_day(ticker.split('.')[0])