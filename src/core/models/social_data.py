"""
CORE DATA MODELS
================

Définit les structures de données du système
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class Platform(Enum):
    """Plateformes sociales supportées"""
    REDDIT = "reddit"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"


class BusinessCategory(Enum):
    """Catégories business pour classification"""
    TECHNOLOGY = "technology"
    FASHION = "fashion"
    GAMING = "gaming"
    BUSINESS = "business"
    ENTERTAINMENT = "entertainment"


@dataclass
class SocialPost:
    """
    Représentation d'un post social media
    
    Attributes:
        id: Identifiant unique
        platform: Plateforme source
        content: Contenu texte
        author: Auteur du post
        author_followers: Nombre de followers
        created_at: Date création
        url: URL du post
        metrics: Métriques engagement
        category: Catégorie business
        metadata: Données additionnelles
        
        # Enrichi par analyse
        sentiment: Catégorie sentiment
        sentiment_score: Score [-1, 1]
        engagement_rate: Taux engagement
        business_potential: Score potentiel [0-10]
    """
    
    # Données de base
    id: str
    platform: Platform
    content: str
    author: str
    author_followers: int
    created_at: datetime
    url: str
    metrics: Dict[str, int]
    category: BusinessCategory
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Données enrichies (après analyse)
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    engagement_rate: Optional[float] = None
    business_potential: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire pour JSON"""
        return {
            'id': self.id,
            'platform': self.platform.value,
            'content': self.content,
            'author': self.author,
            'author_followers': self.author_followers,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else str(self.created_at),
            'url': self.url,
            'metrics': self.metrics,
            'category': self.category.value,
            'metadata': self.metadata,
            'sentiment': self.sentiment,
            'sentiment_score': self.sentiment_score,
            'engagement_rate': self.engagement_rate,
            'business_potential': self.business_potential
        }
    
    def __repr__(self) -> str:
        return (
            f"SocialPost(id='{self.id}', platform={self.platform.value}, "
            f"author='{self.author}', sentiment='{self.sentiment}')"
        )


@dataclass
class Trend:
    """
    Représentation d'une tendance détectée
    
    Attributes:
        name: Nom de la tendance
        volume: Nombre de mentions
        growth_24h: Croissance 24h (ratio)
        sentiment_distribution: Répartition sentiments
        key_phrases: Phrases-clés associées
        platforms: Plateformes sources
        category: Catégorie business
        confidence: Niveau confiance [0-1]
        market_opportunity: Score opportunité [0-100]
        detected_at: Date détection
    """
    
    name: str
    volume: int
    growth_24h: float
    sentiment_distribution: Dict[str, int]
    key_phrases: list
    platforms: list
    category: BusinessCategory
    confidence: float
    market_opportunity: int
    detected_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire"""
        return {
            'name': self.name,
            'volume': self.volume,
            'growth_24h': self.growth_24h,
            'sentiment_distribution': self.sentiment_distribution,
            'key_phrases': self.key_phrases,
            'platforms': self.platforms,
            'category': self.category.value,
            'confidence': self.confidence,
            'market_opportunity': self.market_opportunity,
            'detected_at': self.detected_at.isoformat()
        }