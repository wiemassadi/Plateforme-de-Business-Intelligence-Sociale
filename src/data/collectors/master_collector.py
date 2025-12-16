"""
MASTER COLLECTOR - ORCHESTRATEUR MULTIPROCESSING
=================================================

Responsabilités:
1. Créer 4 processus parallèles (1 par plateforme)
2. Synchroniser la collecte simultanée
3. Agréger les résultats
4. Gérer les erreurs et timeouts
5. Calculer les métriques de performance

Technique clé: ProcessPoolExecutor
"""

import logging
from datetime import datetime
from typing import List, Dict, Any
from concurrent.futures import ProcessPoolExecutor, as_completed, TimeoutError
import time
import multiprocessing
from collections import Counter

from src.core.models.social_data import SocialPost, Platform, BusinessCategory
from src.data.collectors.reddit_collector import DynamicRedditCollector
from src.data.collectors.twitter_collector import DynamicTwitterCollector
from src.data.collectors.instagram_collector import DynamicInstagramCollector
from src.data.collectors.tiktok_collector import DynamicTikTokCollector


class MasterCollector:
    """
    Orchestrateur principal utilisant le VÉRITABLE MULTIPROCESSING
    
    Architecture:
    - 4 processus OS indépendants (contourne GIL Python)
    - Chaque processus a sa propre mémoire
    - Communication via Queue + Pipes
    - Synchronisation via Future objects
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cpu_count = multiprocessing.cpu_count()
        
        # Statistiques de performance
        self.stats = {
            'total_collections': 0,
            'total_posts': 0,
            'average_time': 0,
            'platform_stats': {},
            'error_count': 0
        }
        
        self.logger.info(f"🎯 Master Collector initialisé")
        self.logger.info(f"⚙️  CPUs disponibles: {self.cpu_count}")
        self.logger.info(f"🔧 Max workers: min(4, {self.cpu_count}) = {min(4, self.cpu_count)}")
    
    def collect_all_platforms_parallel(self) -> List[SocialPost]:
        """
        COLLECTE PARALLÈLE DES 4 PLATEFORMES
        
        Flux:
        1. Créer 4 processus via ProcessPoolExecutor
        2. Soumettre les tâches de collecte
        3. Attendre résultats avec timeout 
        4. Agréger et retourner
        
        Returns:
            Liste de SocialPost collectés de toutes plateformes
        """
        all_posts = []
        start_time = time.time()
        
        self.logger.info("=" * 70)
        self.logger.info("🚀 DÉMARRAGE COLLECTE MULTI-PLATEFORMES (MULTIPROCESSING)")
        self.logger.info("=" * 70)
        
        # Configuration ProcessPoolExecutor
        max_workers = min(4, self.cpu_count)
        try:
            # CRÉATION DU POOL DE PROCESSUS
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                # SOUMISSION DES TÂCHES (non-bloquant)
                future_to_platform = {
                    executor.submit(collect_reddit_wrapper): 'Reddit',
                    executor.submit(collect_twitter_wrapper): 'Twitter',
                    executor.submit(collect_instagram_wrapper): 'Instagram',
                    executor.submit(collect_tiktok_wrapper): 'TikTok',
                }
                self.logger.info(f"📡 4 processus lancés en parallèle...")
                
                # COLLECTE DES RÉSULTATS (avec timeout)
                completed = 0
                for future in as_completed(future_to_platform, timeout=120):
                    platform_name = future_to_platform[future]
                    
                    try:
                        # Récupérer résultat du processus
                        platform_posts = future.result(timeout=30)
                        all_posts.extend(platform_posts)
                        completed += 1
                        
                        # Log succès
                        self.logger.info(
                            f"✅ [{completed}/4] {platform_name:12} → "
                            f"{len(platform_posts):3} posts collectés"
                        )
                        
                        # Mettre à jour statistiques
                        self._update_platform_stats(platform_name, len(platform_posts))
                        
                    except TimeoutError:
                        self.logger.error(f"⏱️  {platform_name}: TIMEOUT (> 30s)")
                        self.stats['error_count'] += 1
                        
                      
                        
                    except Exception as e:
                        self.logger.error(f"❌ {platform_name}: ERREUR - {e}")
                        self.stats['error_count'] += 1
                     
        
        except Exception as e:
            self.logger.critical(f"💥 ERREUR CRITIQUE ProcessPoolExecutor: {e}")
            return []
        
        # CALCUL DES MÉTRIQUES DE PERFORMANCE
        collection_time = time.time() - start_time
        self._log_performance_metrics(all_posts, collection_time)
        
        # Mise à jour statistiques globales
        self.stats['total_collections'] += 1
        self.stats['total_posts'] += len(all_posts)
        self.stats['average_time'] = (
            (self.stats['average_time'] * (self.stats['total_collections'] - 1) + collection_time)
            / self.stats['total_collections']
        )
        
        return all_posts
    
    def _update_platform_stats(self, platform: str, count: int):
        """Met à jour les statistiques par plateforme"""
        if platform not in self.stats['platform_stats']:
            self.stats['platform_stats'][platform] = {
                'total_posts': 0,
                'collections': 0
            }
        
        self.stats['platform_stats'][platform]['total_posts'] += count
        self.stats['platform_stats'][platform]['collections'] += 1
    
    def _log_performance_metrics(self, posts: List[SocialPost], time_elapsed: float):
        """Affiche les métriques de performance détaillées"""
        
        self.logger.info("=" * 70)
        self.logger.info("📊 RÉSULTATS COLLECTE PARALLÈLE")
        self.logger.info("=" * 70)
        
        # Statistiques globales
        self.logger.info(f"✨ Posts collectés: {len(posts)}")
        self.logger.info(f"⏱️  Temps total: {time_elapsed:.2f}s")
        self.logger.info(f"⚡ Throughput: {len(posts)/time_elapsed:.1f} posts/sec")
        
        # Speedup théorique
        sequential_time = time_elapsed * 4  # Si séquentiel
        speedup = sequential_time / time_elapsed
        self.logger.info(f"🚀 Speedup: {speedup:.2f}× (vs séquentiel)")
        
        # Distribution par plateforme
        platform_counts = Counter(post.platform.value for post in posts)
        self.logger.info("📍 Distribution par plateforme:")
        for platform, count in platform_counts.items():
            percentage = (count / len(posts) * 100) if posts else 0
            self.logger.info(f"   • {platform:12} → {count:3} posts ({percentage:.1f}%)")
        
        # Distribution par catégorie
        category_counts = Counter(post.category.value for post in posts)
        self.logger.info("🏷️  Distribution par catégorie:")
        for category, count in category_counts.items():
            percentage = (count / len(posts) * 100) if posts else 0
            self.logger.info(f"   • {category:15} → {count:3} posts ({percentage:.1f}%)")
        
        self.logger.info("=" * 70)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques globales du collecteur"""
        return {
            **self.stats,
            'cpu_count': self.cpu_count,
            'max_workers': min(4, self.cpu_count)
        }


# ============================================
# FONCTIONS WRAPPER POUR MULTIPROCESSING
# ============================================
# Ces fonctions s'exécutent dans des processus séparés

def collect_reddit_wrapper() -> List[SocialPost]:
    """Process 1: Collecte Reddit"""
    try:
        collector = DynamicRedditCollector()
        return collector.collect_business_data()
    except Exception as e:
        logging.error(f"Erreur processus Reddit: {e}")
        return []

def collect_twitter_wrapper() -> List[SocialPost]:
    """Process 2: Collecte Twitter"""
    try:
        collector = DynamicTwitterCollector()
        return collector.collect_business_trends()
    except Exception as e:
        logging.error(f"Erreur processus Twitter: {e}")
        return []

def collect_instagram_wrapper() -> List[SocialPost]:
    """Process 3: Collecte Instagram"""
    try:
        collector = DynamicInstagramCollector()
        return collector.collect_business_posts()
    except Exception as e:
        logging.error(f"Erreur processus Instagram: {e}")
        return []

def collect_tiktok_wrapper() -> List[SocialPost]:
    """Process 4: Collecte TikTok"""
    try:
        collector = DynamicTikTokCollector()
        return collector.collect_trending_content()
    except Exception as e:
        logging.error(f"Erreur processus TikTok: {e}")
        return []


# ============================================
# TEST UNITAIRE
# ============================================

if __name__ == "__main__":
    # Configuration logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("\n" + "=" * 70)
    print("🧪 TEST MASTER COLLECTOR - MULTIPROCESSING")
    print("=" * 70)
    
    # Créer le collecteur
    master = MasterCollector()
    
    # Lancer 3 cycles de collecte pour tester
    for cycle in range(3):
        print(f"\n📊 CYCLE {cycle + 1}/3")
        
        posts = master.collect_all_platforms_parallel()
        
        print(f"\n✅ Cycle {cycle + 1} terminé: {len(posts)} posts")
        print("-" * 70)
        
        # Pause entre cycles
        if cycle < 2:
            time.sleep(5)
    
    # Afficher statistiques globales
    stats = master.get_statistics()
    print("\n" + "=" * 70)
    print("📈 STATISTIQUES FINALES")
    print("=" * 70)
    print(f"Total collectes: {stats['total_collections']}")
    print(f"Total posts: {stats['total_posts']}")
    print(f"Temps moyen: {stats['average_time']:.2f}s")
    print(f"Erreurs: {stats['error_count']}")
    print("=" * 70)