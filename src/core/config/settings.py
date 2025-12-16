"""
CONFIGURATION SYSTÈME
=====================
"""

import os
from dataclasses import dataclass


@dataclass
class AnalysisConfig:
    """Configuration analyse"""
    update_interval: int = 30  # secondes entre cycles
    max_workers: int = 4  # threads pour analyse
    trend_threshold: float = 0.5  # seuil détection tendance
    sentiment_batch_size: int = 50  # posts par batch


@dataclass
class Config:
    """Configuration globale"""
    
    # Flask
    secret_key: str = "social-intelligence-secret-key-2024"
    debug: bool = True
    
    # Analyse
    analysis = AnalysisConfig()
    
    # API (pour future expansion)
    api = {
        'twitter': {
            'bearer_token': os.getenv('TWITTER_BEARER_TOKEN', '')
        }
    }


# Instance globale
config = Config()