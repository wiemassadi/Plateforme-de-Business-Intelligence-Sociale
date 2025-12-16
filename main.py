"""
POINT D'ENTRÉE PRINCIPAL
"""

import sys
import os

# Ajouter src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Lancer dashboard
from dashboard.app import app, socketio

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)