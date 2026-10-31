---
kind: external_dependency
name: Scikit-learn ML Library
slug: scikit-learn
category: external_dependency
category_hints:
    - sdk_real_api
scope:
    - '**'
---

### Scikit-learn Machine Learning Library
- **Role**: AI/ML engine for anomaly detection and attack classification using two models: IsolationForest for anomaly scoring and RandomForest for attack type prediction
- **Integration**: `core/threat_detection.py.ThreatDetector` class encapsulates both models; models are trained on synthetic data at startup and persisted as pickle files in `data/models/`
- **Training pipeline**: Bootstraps with 2000 synthetic samples per class; rule-based classifier labels attack samples before RandomForest training; models cached between runs via pickle serialization
- **Attack types supported**: Malware, Ransomware, DDoS, Brute Force, SQL Injection, XSS, Phishing, Insider Threat, Credential Theft, Port Scan