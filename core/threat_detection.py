"""
AI Threat Detection – anomaly detection, classification, severity scoring
Uses a lightweight IsolationForest + rule-based classifier trained on simulated features.
"""
import numpy as np
import pickle
from pathlib import Path
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from utils.config import ATTACK_TYPES, SEVERITY_LEVELS

MODEL_DIR = Path(__file__).parent.parent / "data" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


class ThreatDetector:
    def __init__(self):
        self.anomaly_model = IsolationForest(
            n_estimators=100, contamination=0.3, random_state=42
        )
        self.classifier = RandomForestClassifier(
            n_estimators=50, random_state=42, max_depth=8
        )
        self._trained = False
        self._load_or_train()

    # ── bootstrap training on synthetic data ──────────────────
    def _load_or_train(self):
        model_path = MODEL_DIR / "anomaly_model.pkl"
        clf_path = MODEL_DIR / "classifier.pkl"
        if model_path.exists() and clf_path.exists():
            with open(model_path, "rb") as f:
                self.anomaly_model = pickle.load(f)
            with open(clf_path, "rb") as f:
                self.classifier = pickle.load(f)
            self._trained = True
        else:
            self._train()

    def _train(self):
        np.random.seed(42)
        n = 2000
        # Features: packets_per_sec, failed_logins, payload_size, unique_ports, entropy
        normal = np.column_stack([
            np.random.normal(50, 15, n),
            np.random.poisson(1, n),
            np.random.normal(500, 100, n),
            np.random.poisson(3, n),
            np.random.uniform(2, 5, n),
        ])
        attack = np.column_stack([
            np.random.normal(500, 200, n),
            np.random.poisson(20, n),
            np.random.normal(5000, 2000, n),
            np.random.poisson(50, n),
            np.random.uniform(6, 8, n),
        ])
        X = np.vstack([normal, attack])
        self.anomaly_model.fit(X)

        # Train classifier on labelled synthetic data
        labels = []
        for row in attack:
            labels.append(self._rule_classify(row))
        # Normal traffic labelled as "Normal" (index -1 means no attack, but we skip)
        attack_labels = np.array(labels)
        self.classifier.fit(attack, attack_labels)

        with open(MODEL_DIR / "anomaly_model.pkl", "wb") as f:
            pickle.dump(self.anomaly_model, f)
        with open(MODEL_DIR / "classifier.pkl", "wb") as f:
            pickle.dump(self.classifier, f)
        self._trained = True

    @staticmethod
    def _rule_classify(features):
        pps, failed, payload, ports, entropy = features
        if failed > 15 and ports < 5:
            return "Brute Force"
        if ports > 40:
            return "Port Scan"
        if payload > 6000 and entropy > 7:
            return "Ransomware"
        if pps > 800:
            return "DDoS"
        if payload > 4000 and "SELECT" in str(int(payload)):
            return "SQL Injection"
        # Spam: low payload, low ports, moderate traffic – bulk unsolicited messages
        if payload < 1500 and ports < 5 and pps < 200 and entropy < 5:
            return "Spam"
        if entropy > 7:
            return np.random.choice(["Malware", "Ransomware", "XSS"])
        return np.random.choice(ATTACK_TYPES)

    # ── Public API ────────────────────────────────────────────
    def analyze(self, features: dict) -> dict:
        """
        features: dict with keys packets_per_sec, failed_logins, payload_size,
                  unique_ports, entropy
        Returns: dict with attack_type, severity, confidence, is_anomaly
        """
        vec = np.array([[
            features.get("packets_per_sec", 0),
            features.get("failed_logins", 0),
            features.get("payload_size", 0),
            features.get("unique_ports", 0),
            features.get("entropy", 3.0),
        ]])

        anomaly_score = self.anomaly_model.decision_function(vec)[0]
        is_anomaly = self.anomaly_model.predict(vec)[0] == -1

        if is_anomaly:
            try:
                attack_type = self.classifier.predict(vec)[0]
            except Exception:
                attack_type = np.random.choice(ATTACK_TYPES)
            confidence = min(1.0, max(0.4, 1.0 - abs(anomaly_score)))
        else:
            attack_type = "Normal"
            confidence = min(1.0, max(0.5, 0.5 + anomaly_score))

        severity = self._score_severity(features, is_anomaly, confidence)

        return {
            "is_anomaly": is_anomaly,
            "attack_type": attack_type,
            "severity": severity,
            "confidence": round(confidence, 3),
            "anomaly_score": round(anomaly_score, 4),
        }

    @staticmethod
    def _score_severity(features, is_anomaly, confidence):
        if not is_anomaly:
            return "Low"
        score = confidence * 100
        if features.get("failed_logins", 0) > 20:
            score += 15
        if features.get("packets_per_sec", 0) > 800:
            score += 20
        if features.get("entropy", 0) > 7:
            score += 10
        if score >= 90:
            return "Critical"
        if score >= 70:
            return "High"
        if score >= 45:
            return "Medium"
        return "Low"
