"""
SENTIMENT ANALYZER - ANALYSE MULTITHREADING
============================================

Responsabilités:
1. Analyser sentiments avec 2 moteurs IA (TextBlob + VADER)
2. Traiter posts en parallèle via ThreadPoolExecutor
3. Enrichir posts avec scores sentiment
4. Calculer statistiques agrégées
5. Classifier en 5 catégories (très positif → très négatif)

Technique clé: ThreadPoolExecutor + Pipeline IA
"""

import logging
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
import time
from datetime import datetime

# NLP Libraries
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from src.core.models.social_data import SocialPost


class SentimentAnalyzer:
    """
    Analyseur de sentiment utilisant MULTITHREADING
    
    Architecture:
    - ThreadPoolExecutor: 4-8 threads parallèles
    - 2 moteurs IA combinés: TextBlob + VADER
    - Scoring hybride pour meilleure précision
    """
    
    def __init__(self, max_workers: int = 4):
        self.logger = logging.getLogger(__name__)
        self.max_workers = max_workers
        
        # Initialiser les moteurs IA
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Statistiques
        self.stats = {
            'total_analyzed': 0,
            'average_time': 0,
            'analysis_count': 0
        }
        
        self.logger.info(f"Sentiment Analyzer initialisé")
        self.logger.info(f"  Threads: {max_workers}")
        self.logger.info(f" Moteurs IA: TextBlob + VADER")
    
    def analyze_batch(self, posts: List[SocialPost]) -> List[SocialPost]:
        """
        ANALYSE EN PARALLÈLE D'UN BATCH DE POSTS
        
        Stratégie:
        1. Diviser posts en chunks (50 posts/chunk)
        2. Créer 1 thread par chunk
        3. Chaque thread analyse son chunk
        4. Agréger résultats
        
        Args:
            posts: Liste de posts à analyser
            
        Returns:
            Posts enrichis avec sentiment
        """
        if not posts:
            return []
        
        start_time = time.time()
        analyzed_posts = []
        self.logger.info(f"🧠 ANALYSE SENTIMENT: {len(posts)} posts")
        # Diviser en chunks pour parallélisation
        chunk_size = 50
        chunks = [posts[i:i + chunk_size] for i in range(0, len(posts), chunk_size)]
        self.logger.info(f"📦 Division: {len(chunks)} chunks de ~{chunk_size} posts")
        try:
            # CRÉATION DU POOL DE THREADS
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # SOUMISSION DES TÂCHES
                future_to_chunk = {
                    executor.submit(self._analyze_chunk, chunk, idx): idx
                    for idx, chunk in enumerate(chunks)
                }
                # COLLECTE DES RÉSULTATS
                completed = 0
                for future in as_completed(future_to_chunk):
                    chunk_idx = future_to_chunk[future]
                    try:
                        chunk_results = future.result()
                        analyzed_posts.extend(chunk_results)
                        completed += 1
                        
                        self.logger.info(
                            f"✅ [{completed}/{len(chunks)}] Chunk {chunk_idx} → "
                            f"{len(chunk_results)} posts analysés"
                        )
                        
                    except Exception as e:
                        self.logger.error(f"❌ Erreur chunk {chunk_idx}: {e}")
        
        except Exception as e:
            self.logger.error(f"💥 Erreur ThreadPoolExecutor: {e}")
            return posts  # Retourner posts non analysés
        
        # CALCUL MÉTRIQUES
        analysis_time = time.time() - start_time
        self._log_analysis_metrics(analyzed_posts, analysis_time)
        
        # Mise à jour statistiques
        self.stats['total_analyzed'] += len(analyzed_posts)
        self.stats['analysis_count'] += 1
        self.stats['average_time'] = (
            (self.stats['average_time'] * (self.stats['analysis_count'] - 1) + analysis_time)
            / self.stats['analysis_count']
        )
        
        return analyzed_posts
    
    def _analyze_chunk(self, chunk: List[SocialPost], chunk_idx: int) -> List[SocialPost]:
        """
        Analyse un chunk de posts (exécuté dans un thread)
        
        Args:
            chunk: Liste de posts à analyser
            chunk_idx: Index du chunk (pour logging)
            
        Returns:
            Posts enrichis avec sentiment
        """
        analyzed = []
        for post in chunk:
            try:
                # ANALYSE HYBRIDE: TextBlob + VADER
                sentiment_score = self._hybrid_sentiment_analysis(post.content)
                # Classification en catégories
                sentiment_label = self._classify_sentiment(sentiment_score)
                # Enrichir le post
                post.sentiment = sentiment_label
                post.sentiment_score = sentiment_score
                # Calculer engagement rate
                post.engagement_rate = self._calculate_engagement(post)
                # Calculer business potential
                post.business_potential = self._calculate_business_potential(post)
                analyzed.append(post)
            except Exception as e:
                self.logger.debug(f"Erreur analyse post {post.id}: {e}")
                # Ajouter sans analyse en cas d'erreur
                post.sentiment = 'neutral'
                post.sentiment_score = 0.0
                analyzed.append(post)
        return analyzed
    
    def _hybrid_sentiment_analysis(self, text: str) -> float:
        """
        ANALYSE HYBRIDE: TextBlob + VADER
        
        Combine 2 moteurs pour meilleure précision:
        - TextBlob: Bon pour texte général
        - VADER: Optimisé pour réseaux sociaux (emojis, slang)
        
        Args:
            text: Texte à analyser
            
        Returns:
            Score sentiment [-1, 1]
        """
        if not text:
            return 0.0
        
        try:
            # 1. TEXTBLOB ANALYSIS
            blob = TextBlob(text)
            textblob_score = blob.sentiment.polarity  # [-1, 1]
            
            # 2. VADER ANALYSIS
            vader_scores = self.vader_analyzer.polarity_scores(text)
            vader_score = vader_scores['compound']  # [-1, 1]
            
            # 3. SCORE HYBRIDE (moyenne pondérée)
            # VADER: 60% (meilleur pour social media)
            # TextBlob: 40% (meilleur pour texte formel)
            hybrid_score = (vader_score * 0.6) + (textblob_score * 0.4)
            
            return hybrid_score
            
        except Exception as e:
            self.logger.debug(f"Erreur analyse sentiment: {e}")
            return 0.0
    
    def _classify_sentiment(self, score: float) -> str:
        """
        Classification en 5 catégories
        
        Échelle:
        - very_positive: > 0.5
        - positive: 0.1 à 0.5
        - neutral: -0.1 à 0.1
        - negative: -0.5 à -0.1
        - very_negative: < -0.5
        """
        if score > 0.5:
            return 'very_positive'
        elif score > 0.1:
            return 'positive'
        elif score > -0.1:
            return 'neutral'
        elif score > -0.5:
            return 'negative'
        else:
            return 'very_negative'
    
    def _calculate_engagement(self, post: SocialPost) -> float:
        """
        Calcule le taux d'engagement
        
        Formula:
        Engagement = (Likes + Comments + Shares) / Followers
        """
        metrics = post.metrics
        followers = post.author_followers or 1
        
        total_engagement = (
            metrics.get('likes', 0) +
            metrics.get('comments', 0) +
            metrics.get('shares', 0) +
            metrics.get('retweets', 0)
        )
        
        return min(total_engagement / followers, 1.0)  # Cap à 1.0
    
    def _calculate_business_potential(self, post: SocialPost) -> int:
        """
        Score de potentiel business [0-10]
        
        Facteurs:
        - Engagement rate (40%)
        - Sentiment positif (30%)
        - Nombre de followers (20%)
        - Viralité (10%)
        """
        # Engagement
        engagement_score = (post.engagement_rate or 0) * 40
        
        # Sentiment
        sentiment_bonus = 0
        if post.sentiment in ['very_positive', 'positive']:
            sentiment_bonus = 30
        elif post.sentiment == 'neutral':
            sentiment_bonus = 15
        
        # Followers
        followers = post.author_followers or 0
        follower_score = min(followers / 100000, 1.0) * 20  # Max à 100K followers
        
        # Viralité (based on metrics)
        likes = post.metrics.get('likes', 0)
        virality_score = min(likes / 10000, 1.0) * 10  # Max à 10K likes
        
        total_score = engagement_score + sentiment_bonus + follower_score + virality_score
        
        return int(min(total_score / 10, 10))  # Normaliser sur 10
    
    def get_sentiment_summary(self, posts: List[SocialPost]) -> Dict[str, Any]:
        """
        Génère un résumé des sentiments
        
        Returns:
            Dictionnaire avec statistiques agrégées
        """
        if not posts:
            return {
                'total': 0,
                'very_positive': 0,
                'positive': 0,
                'neutral': 0,
                'negative': 0,
                'very_negative': 0,
                'percentages': {},
                'average_score': 0.0
            }
        
        # Compter par catégorie
        sentiment_counts = Counter(post.sentiment for post in posts if hasattr(post, 'sentiment'))
        total = len(posts)
        
        # Calculer pourcentages
        percentages = {
            sentiment: (count / total * 100)
            for sentiment, count in sentiment_counts.items()
        }
        
        # Score moyen
        scores = [post.sentiment_score for post in posts if hasattr(post, 'sentiment_score')]
        average_score = sum(scores) / len(scores) if scores else 0.0
        
        return {
            'total': total,
            'very_positive': sentiment_counts.get('very_positive', 0),
            'positive': sentiment_counts.get('positive', 0),
            'neutral': sentiment_counts.get('neutral', 0),
            'negative': sentiment_counts.get('negative', 0),
            'very_negative': sentiment_counts.get('very_negative', 0),
            'percentages': percentages,
            'average_score': average_score,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_sentiment_by_category(self, posts: List[SocialPost]) -> Dict[str, Dict]:
        """
        Statistiques sentiment par catégorie business
        """
        category_sentiments = {}
        
        for post in posts:
            if not hasattr(post, 'sentiment'):
                continue
            
            category = post.category.value
            if category not in category_sentiments:
                category_sentiments[category] = {
                    'positive': 0,
                    'neutral': 0,
                    'negative': 0,
                    'total': 0
                }
            
            category_sentiments[category]['total'] += 1
            
            if post.sentiment in ['very_positive', 'positive']:
                category_sentiments[category]['positive'] += 1
            elif post.sentiment == 'neutral':
                category_sentiments[category]['neutral'] += 1
            else:
                category_sentiments[category]['negative'] += 1
        
        return category_sentiments
    
    def _log_analysis_metrics(self, posts: List[SocialPost], time_elapsed: float):
        """Affiche les métriques d'analyse"""
        
        self.logger.info("=" * 70)
        self.logger.info("📊 RÉSULTATS ANALYSE SENTIMENT")
        self.logger.info("=" * 70)
        
        self.logger.info(f"✨ Posts analysés: {len(posts)}")
        self.logger.info(f"⏱️  Temps: {time_elapsed:.2f}s")
        self.logger.info(f"⚡ Vitesse: {len(posts)/time_elapsed:.1f} posts/sec")
        
        # Speedup vs séquentiel
        sequential_time = len(posts) * 0.05  # ~50ms par post
        speedup = sequential_time / time_elapsed if time_elapsed > 0 else 0
        self.logger.info(f"🚀 Speedup: {speedup:.2f}× (vs séquentiel)")
        
        # Distribution sentiments
        summary = self.get_sentiment_summary(posts)
        self.logger.info("😊 Distribution sentiments:")
        for sentiment in ['very_positive', 'positive', 'neutral', 'negative', 'very_negative']:
            count = summary[sentiment]
            percentage = summary['percentages'].get(sentiment, 0)
            self.logger.info(f"   • {sentiment:15} → {count:3} posts ({percentage:.1f}%)")
        
        self.logger.info(f"📈 Score moyen: {summary['average_score']:.3f}")
        self.logger.info("=" * 70)


# ============================================
# TEST UNITAIRE
# ============================================

if __name__ == "__main__":
    from src.core.models.social_data import Platform, BusinessCategory
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("\n🧪 TEST SENTIMENT ANALYZER - MULTITHREADING\n")
    
    # Créer posts de test
    test_posts = []
    test_texts = [
        "This product is absolutely amazing! Best purchase ever! 😍",
        "Terrible quality, very disappointed. Would not recommend. 😠",
        "It's okay, nothing special. Just average product.",
        "Love it! Great value for money. Highly recommended! ⭐⭐⭐⭐⭐",
        "Waste of money. Cheap and breaks easily. Avoid! 👎"
    ]
    
    for i, text in enumerate(test_texts * 40):  # 200 posts total
        post = SocialPost(
            id=f"test_{i}",
            platform=Platform.TWITTER,
            content=text,
            author=f"@user{i}",
            author_followers=10000,
            created_at=datetime.now(),
            url=f"https://test.com/{i}",
            metrics={'likes': 100, 'comments': 10},
            category=BusinessCategory.TECHNOLOGY
        )
        test_posts.append(post)
    
    # Créer analyzer
    analyzer = SentimentAnalyzer(max_workers=4)
    
    # Analyser
    print(f"📊 Analyse de {len(test_posts)} posts...\n")
    analyzed = analyzer.analyze_batch(test_posts)
    
    # Afficher résumé
    print("\n📈 RÉSUMÉ:")
    summary = analyzer.get_sentiment_summary(analyzed)
    for key, value in summary.items():
        if key != 'percentages':
            print(f"  {key}: {value}")
    
    # Exemples
    print("\n📝 EXEMPLES:")
    for post in analyzed[:3]:
        print(f"  Text: {post.content[:50]}...")
        print(f"  Sentiment: {post.sentiment} (score: {post.sentiment_score:.3f})")
        print(f"  Business: {post.business_potential}/10")
        print()