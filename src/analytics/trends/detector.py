"""
TREND DETECTOR - DÉTECTION TENDANCES BUSINESS
==============================================
"""

import logging
from typing import List, Dict
from collections import Counter, defaultdict
from datetime import datetime
import re

from src.core.models.social_data import SocialPost, Trend, BusinessCategory


class TrendDetector:
    """Détecte les tendances business émergentes"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.previous_volumes = defaultdict(int)
    
    def detect_business_trends(self, posts: List[SocialPost]) -> List[Trend]:
        """
        Détecte les tendances dans les posts
        
        Algorithme:
        1. Extraire mots-clés fréquents
        2. Calculer croissance vs cycle précédent
        3. Analyser sentiment par tendance
        4. Scorer opportunité business
        """
        if not posts:
            return []
        
        self.logger.info(f"🔍 Détection tendances sur {len(posts)} posts")
        
        # Extraire keywords
        keywords = self._extract_keywords(posts)
        
        # Détecter tendances
        trends = []
        for keyword, data in keywords.items():
            if data['count'] < 5:  # Min 5 mentions
                continue
            
            # Calculer croissance
            previous_volume = self.previous_volumes[keyword]
            growth = self._calculate_growth(data['count'], previous_volume)
            
            # Seuil détection: +50% croissance ou volume > 20
            if growth > 0.5 or data['count'] > 20:
                trend = self._create_trend(keyword, data, growth, posts)
                trends.append(trend)
        
        # Mettre à jour historique
        for keyword, data in keywords.items():
            self.previous_volumes[keyword] = data['count']
        
        # Trier par opportunité
        trends.sort(key=lambda t: t.market_opportunity, reverse=True)
        
        self.logger.info(f"✅ {len(trends)} tendances détectées")
        
        return trends[:10]  # Top 10
    
    def _extract_keywords(self, posts: List[SocialPost]) -> Dict:
        """Extrait mots-clés importants"""
        keywords = defaultdict(lambda: {
            'count': 0,
            'sentiments': [],
            'categories': [],
            'platforms': set(),
            'phrases': []
        })
        
        # Mots-clés à chercher
        important_words = {
            'AI', 'blockchain', 'crypto', 'NFT', 'metaverse',
            'sustainable', 'eco', 'climate', 'green',
            'remote', 'hybrid', 'startup', 'SaaS',
            'gaming', 'esports', 'streaming',
            'fashion', 'vintage', 'thrift'
        }
        
        for post in posts:
            text = post.content.lower()
            
            # Chercher mots-clés
            for word in important_words:
                if word.lower() in text:
                    keywords[word]['count'] += 1
                    if hasattr(post, 'sentiment'):
                        keywords[word]['sentiments'].append(post.sentiment)
                    keywords[word]['categories'].append(post.category)
                    keywords[word]['platforms'].add(post.platform.value)
                    
                    # Extraire phrase contexte
                    match = re.search(
                        rf'.{{0,30}}{re.escape(word.lower())}.{{0,30}}',
                        text
                    )
                    if match:
                        keywords[word]['phrases'].append(match.group())
        
        return dict(keywords)
#calcule de la croissance
    def _calculate_growth(self, current: int, previous: int) -> float:
        """Calcule croissance"""
        if previous == 0:
            return 1.0 if current > 0 else 0.0
        return (current - previous) / previous
    
    def _create_trend(self, keyword: str, data: Dict, growth: float, posts: List[SocialPost]) -> Trend:
        """Crée objet Trend"""
        
        # Distribution sentiments
        sentiment_dist = Counter(data['sentiments'])
        
        # Catégorie dominante
        category_counts = Counter(data['categories'])
        dominant_category = category_counts.most_common(1)[0][0]
        
        # Confiance (basé sur volume)
        confidence = min(data['count'] / 50, 1.0)
        
        # Opportunité market
        positive_ratio = (
            sentiment_dist.get('very_positive', 0) +
            sentiment_dist.get('positive', 0)
        ) / max(sum(sentiment_dist.values()), 1)
        
        market_score = int(
            (growth * 30) +  # Croissance
            (positive_ratio * 40) +  # Sentiment positif
            (confidence * 30)  # Volume
        )
        
        return Trend(
            name=keyword.upper(),
            volume=data['count'],
            growth_24h=growth,
            sentiment_distribution=dict(sentiment_dist),
            key_phrases=data['phrases'][:3],
            platforms=list(data['platforms']),
            category=dominant_category,
            confidence=confidence,
            market_opportunity=min(market_score, 100),
            detected_at=datetime.now()
        )