import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from typing import List, Dict, Any, Optional
import joblib # For saving/loading the model (optional for prototype, but good practice)

class AnomalyDetector:
    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        """
        Initializes the Isolation Forest Anomaly Detector.

        Args:
            contamination: The proportion of outliers in the data set. Used when fitting
                           the model to define the threshold for anomaly scores.
            random_state: Seed for reproducibility.
        """
        self.model: Optional[IsolationForest] = None
        self.contamination = contamination
        self.random_state = random_state
        self.feature_names: List[str] = []

    def train(self, features_data: List[Dict[str, Any]]) -> None:
        """
        Trains the Isolation Forest model on the provided normal features.

        Args:
            features_data: A list of dictionaries, where each dictionary represents
                           the extracted numerical features of a log entry.
        """
        if not features_data:
            print("No data provided for training the anomaly detector.")
            return

        # Convert list of dicts to DataFrame
        df = pd.DataFrame(features_data)

        # Store feature names to ensure consistent order during prediction
        self.feature_names = df.columns.tolist()

        # Initialize and train the Isolation Forest model
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            # n_estimators=100, # Number of base estimators (trees)
            # max_features=1.0, # Number of features to draw from X to train each base estimator
            # max_samples="auto" # Number of samples to draw from X to train each base estimator
        )
        self.model.fit(df)
        print(f"Anomaly detector trained with {len(features_data)} samples.")

    def predict(self, new_features: Dict[str, Any]) -> float:
        """
        Predicts the anomaly score for a single new set of features.

        Args:
            new_features: A dictionary of numerical features for a single log entry.

        Returns:
            The anomaly score. Lower scores indicate higher anomaly.
            -1 for anomalous, 1 for normal (sklearn default behavior for `predict` method).
            The `decision_function` method gives raw anomaly score.
        """
        if self.model is None:
            print("Model not trained. Cannot predict.")
            return 0.0 # Return a neutral score if model is not trained

        # Ensure new_features have the same order and features as during training
        # If a feature is missing, it will be added with a default value (e.g., 0)
        # If an extra feature exists, it will be ignored.
        feature_vector = [new_features.get(f_name, 0) for f_name in self.feature_names]
        
        # Reshape for single sample prediction
        X = np.array(feature_vector).reshape(1, -1)
        
        # decision_function gives a raw anomaly score, where lower means more anomalous
        # score_samples gives the opposite (higher means more anomalous)
        # We want lower score for more anomalous, so decision_function is suitable.
        anomaly_score = self.model.decision_function(X)[0]
        return anomaly_score

    def save_model(self, filepath: str) -> None:
        """Saves the trained model to a file."""
        if self.model:
            joblib.dump(self.model, filepath)
            print(f"Model saved to {filepath}")

    def load_model(self, filepath: str) -> None:
        """Loads a trained model from a file."""
        try:
            self.model = joblib.load(filepath)
            # Reconstruct feature_names if needed, or save them alongside the model
            # For simplicity, assuming the order will be maintained or handled externally for now.
            print(f"Model loaded from {filepath}")
        except FileNotFoundError:
            print(f"No model found at {filepath}. Will start fresh.")
        except Exception as e:
            print(f"Error loading model: {e}. Will start fresh.")

# Example usage (for testing this module independently)
if __name__ == "__main__":
    # Simulate some normal data (e.g., typical login hours)
    normal_data = [
        {"login_hour": 9, "day_of_week": 1, "is_admin_account": 0, "is_vpn_source": 0, "event_type_authentication": 1, "event_type_file_access": 0, "event_type_process_exec": 0, "event_type_privilege_escalation": 0, "is_weekend":0, "time_of_day_sin":0.5, "time_of_day_cos":0.5, "failed_login_count_5min":0, "device_familiarity_score":0, "geo_location_risk_score":0},
        {"login_hour": 10, "day_of_week": 1, "is_admin_account": 0, "is_vpn_source": 0, "event_type_authentication": 1, "event_type_file_access": 0, "event_type_process_exec": 0, "event_type_privilege_escalation": 0, "is_weekend":0, "time_of_day_sin":0.5, "time_of_day_cos":0.5, "failed_login_count_5min":0, "device_familiarity_score":0, "geo_location_risk_score":0},
        {"login_hour": 17, "day_of_week": 2, "is_admin_account": 0, "is_vpn_source": 0, "event_type_authentication": 1, "event_type_file_access": 0, "event_type_process_exec": 0, "event_type_privilege_escalation": 0, "is_weekend":0, "time_of_day_sin":0.5, "time_of_day_cos":0.5, "failed_login_count_5min":0, "device_familiarity_score":0, "geo_location_risk_score":0},
        {"login_hour": 11, "day_of_week": 3, "is_admin_account": 0, "is_vpn_source": 0, "event_type_authentication": 1, "event_type_file_access": 0, "event_type_process_exec": 0, "event_type_privilege_escalation": 0, "is_weekend":0, "time_of_day_sin":0.5, "time_of_day_cos":0.5, "failed_login_count_5min":0, "device_familiarity_score":0, "geo_location_risk_score":0},
        {"login_hour": 14, "day_of_week": 4, "is_admin_account": 0, "is_vpn_source": 0, "event_type_authentication": 1, "event_type_file_access": 0, "event_type_process_exec": 0, "event_type_privilege_escalation": 0, "is_weekend":0, "time_of_day_sin":0.5, "time_of_day_cos":0.5, "failed_login_count_5min":0, "device_familiarity_score":0, "geo_location_risk_score":0},
    ]

    # Simulate an anomalous data point (e.g., admin login at 3 AM on weekend)
    anomalous_data = {
        "login_hour": 3, "day_of_week": 6, "is_admin_account": 1, "is_vpn_source": 0, "event_type_authentication": 1, "event_type_file_access": 0, "event_type_process_exec": 0, "event_type_privilege_escalation": 0, "is_weekend":1, "time_of_day_sin":0.1, "time_of_day_cos":0.1, "failed_login_count_5min":0, "device_familiarity_score":0, "geo_location_risk_score":0
    }
    
    detector = AnomalyDetector(contamination=0.1) # Expect 10% outliers
    detector.train(normal_data)

    # Predict on normal data
    for i, data in enumerate(normal_data):
        score = detector.predict(data)
        print(f"Normal sample {i} anomaly score: {score:.4f}")

    # Predict on anomalous data
    anomaly_score = detector.predict(anomalous_data)
    print(f"Anomalous sample anomaly score: {anomaly_score:.4f}")

    # Interpretation: Lower score typically means more anomalous.
    # The IsolationForest decision_function gives a score where values closer to 0
    # indicate anomalies, and values closer to 1 (or higher) indicate normal.
    # A common way to interpret is that negative values are anomalies, positive are normal,
    # with the magnitude indicating confidence.