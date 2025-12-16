"""
DASHBOARD FLASK + WEBSOCKET
============================

Application web temps réel avec:
- Flask (serveur web)
- SocketIO (WebSocket)
- Threading (boucle analyse)
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import logging
import threading
import time
from datetime import datetime, timedelta
from collections import Counter

# Imports locaux
from src.data.collectors.master_collector import MasterCollector
from src.analytics.sentiment.analyzer import SentimentAnalyzer
from src.analytics.trends.detector import TrendDetector
from src.core.config.settings import config


# Configuration Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = config.secret_key

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Initialisation composants
master_collector = MasterCollector()
sentiment_analyzer = SentimentAnalyzer(max_workers=4)
trend_detector = TrendDetector()

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================
# ÉTAT SYSTÈME
# ============================================

class SystemState:
    """État global du système"""
    
    def __init__(self):
        self.is_running = False
        self.processed_posts = []
        self.all_posts_history = []
        self.current_trends = []
        self.sentiment_stats = {}
        self.start_time = None
        self.last_update = None
        
        self.performance_metrics = {
            'posts_processed': 0,
            'processing_speed': 0,
            'last_processing_time': 0,
            'total_iterations': 0,
            'system_uptime': 0,
            'platform_stats': {}
        }

system_state = SystemState()


# ============================================
# ROUTES WEB
# ============================================

@app.route('/')
def dashboard():
    """Page principale"""
    return render_template('dashboard.html')

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'is_running': system_state.is_running
    })

@app.route('/api/stats')
def stats():
    """Statistiques système"""
    return jsonify({
        'system': system_state.performance_metrics,
        'sentiment': system_state.sentiment_stats,
        'trends_count': len(system_state.current_trends),
        'is_running': system_state.is_running
    })

@app.route('/api/trends')
def get_trends():
    """Tendances actuelles"""
    return jsonify([t.to_dict() for t in system_state.current_trends])

@app.route('/api/posts/recent')
def recent_posts():
    """Posts récents"""
    limit = min(int(request.args.get('limit', 20)), 100)
    recent = system_state.processed_posts[-limit:]
    return jsonify([p.to_dict() for p in recent])

@app.route('/api/control/start', methods=['POST'])
def start_system():
    """Démarre le système"""
    if not system_state.is_running:
        system_state.is_running = True
        system_state.start_time = datetime.now()
        
        # Lancer thread traitement
        thread = threading.Thread(target=processing_loop, daemon=True)
        thread.start()
        
        logger.info("🚀 SYSTÈME DÉMARRÉ")
        return jsonify({'status': 'started', 'message': 'Système démarré'})
    
    return jsonify({'status': 'already_running'})

@app.route('/api/control/stop', methods=['POST'])
def stop_system():
    """Arrête le système"""
    system_state.is_running = False
    logger.info("⏹️ SYSTÈME ARRÊTÉ")
    return jsonify({'status': 'stopped', 'message': 'Système arrêté'})


# ============================================
# BOUCLE DE TRAITEMENT (THREAD)
# ============================================

def processing_loop():
    """
    Boucle principale - Thread séparé
    
    1. Collecte (Multiprocessing)
    2. Analyse (Multithreading)
    3. Détection tendances
    4. Mise à jour état
    5. Émission WebSocket
    """
    iteration = 0
    
    while system_state.is_running:
        try:
            iteration += 1
            start_time = time.time()
            
            logger.info(f"\n{'='*70}")
            logger.info(f"🔄 ITÉRATION #{iteration}")
            logger.info(f"{'='*70}")
            
            # 1. COLLECTE (Multiprocessing - 4 processus)
            logger.info("📡 Phase 1: Collecte multi-plateformes...")
            collected_posts = master_collector.collect_all_platforms_parallel()
            
            # 2. ANALYSE SENTIMENT (Multithreading - 4 threads)
            logger.info("🧠 Phase 2: Analyse sentiments...")
            analyzed_posts = sentiment_analyzer.analyze_batch(collected_posts)
            
            # 3. DÉTECTION TENDANCES
            logger.info("🔍 Phase 3: Détection tendances...")
            trends = trend_detector.detect_business_trends(analyzed_posts)
            
            # 4. MISE À JOUR ÉTAT
            system_state.all_posts_history.extend(analyzed_posts)
            
            # Fenêtre glissante 24h
            cutoff = datetime.now() - timedelta(hours=24)
            system_state.processed_posts = [
                p for p in system_state.all_posts_history
                if p.created_at >= cutoff
            ]
            
            system_state.current_trends = trends
            system_state.sentiment_stats = sentiment_analyzer.get_sentiment_summary(
                system_state.processed_posts
            )
            system_state.last_update = datetime.now()
            
            # Statistiques plateformes
            platform_stats = Counter(p.platform.value for p in system_state.all_posts_history)
            
            # 5. MÉTRIQUES PERFORMANCE
            elapsed = time.time() - start_time
            system_state.performance_metrics.update({
                'posts_processed': len(system_state.all_posts_history),
                'posts_active_window': len(system_state.processed_posts),
                'processing_speed': len(collected_posts) / elapsed if elapsed > 0 else 0,
                'last_processing_time': round(elapsed, 2),
                'total_iterations': iteration,
                'system_uptime': (datetime.now() - system_state.start_time).total_seconds(),
                'platform_stats': dict(platform_stats)
            })
            
            # 6. ÉMISSION WEBSOCKET
            emit_updates(collected_posts, trends)
            
            logger.info(f"✅ Itération #{iteration} terminée en {elapsed:.2f}s")
            logger.info(f"📊 {len(collected_posts)} nouveaux posts, "
                       f"{len(system_state.all_posts_history)} total, "
                       f"{len(trends)} tendances")
            
            # Nettoyage (garder 7 jours max)
            if iteration % 10 == 0:
                week_ago = datetime.now() - timedelta(days=7)
                before = len(system_state.all_posts_history)
                system_state.all_posts_history = [
                    p for p in system_state.all_posts_history
                    if p.created_at >= week_ago
                ]
                removed = before - len(system_state.all_posts_history)
                if removed > 0:
                    logger.info(f"🧹 Nettoyage: {removed} posts > 7 jours supprimés")
            
            # Pause
            time.sleep(config.analysis.update_interval)
            
        except Exception as e:
            logger.error(f"❌ ERREUR: {e}", exc_info=True)
            time.sleep(30)


# ============================================
# WEBSOCKET
# ============================================

def emit_updates(new_posts, trends):
    """Émet mises à jour via WebSocket"""
    try:
        # Métriques système
        socketio.emit('system_stats', {
            'timestamp': datetime.now().isoformat(),
            **system_state.performance_metrics
        })
        # Sentiments
        socketio.emit('sentiment_update', {
            **system_state.sentiment_stats,
            'has_changed': True
        })
        # Tendances
        socketio.emit('trends_update', {
            'trends': [t.to_dict() for t in trends] if trends else [],
            'count': len(trends),
            'timestamp': datetime.now().isoformat()
        })
        # Nouveaux posts
        if new_posts:
            socketio.emit('new_posts', {
                'posts': [p.to_dict() for p in new_posts[-10:]],
                'count': len(new_posts)
            })
        # Stats collecte
        socketio.emit('collection_stats', {
            'total': system_state.performance_metrics.get('platform_stats', {}),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur WebSocket: {e}")

@socketio.on('connect')
def handle_connect():
    """Client connecté"""
    logger.info(f"👤 Client connecté: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Client déconnecté"""
    logger.info(f"👤 Client déconnecté: {request.sid}")


# ============================================
# LANCEMENT
# ============================================

if __name__ == '__main__':
    logger.info("\n" + "="*70)
    logger.info("🚀 SOCIAL BUSINESS INTELLIGENCE PLATFORM")
    logger.info("="*70)
    logger.info("🌐 Dashboard: http://localhost:5000")
    logger.info("📊 API: http://localhost:5000/api/health")
    logger.info("="*70 + "\n")
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=config.debug,
        use_reloader=False
    )