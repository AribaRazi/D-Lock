# # backend/app.py
# from flask import Flask
# from flask_cors import CORS
# from routes import routes  # your Blueprint from routes.py

# app = Flask(__name__)

# # allow frontend (Vite dev server) to call backend
# CORS(app, resources={r"/api/*": {"origins": "*"}})

# # IMPORTANT: prefix /api to match the frontend
# app.register_blueprint(routes, url_prefix="/api")

# if __name__ == "__main__":
#     app.run(debug=True)  # http://127.0.0.1:5000

# backend/app.py
from flask import Flask
from flask_cors import CORS
from routes import routes
from models import db
import os

app = Flask(__name__)

# ===== DATABASE CONFIGURATION =====
# SQLite database (stored in backend/instance/dlock.db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dlock.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Secret key for session management (change in production!)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-this-in-production')

# ===== INITIALIZE DATABASE =====
db.init_app(app)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()
    print("✅ Database initialized! Tables created if they didn't exist.")

# ===== CORS CONFIGURATION =====
# Allow frontend (Vite dev server) to call backend
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ===== REGISTER BLUEPRINTS =====
# IMPORTANT: prefix /api to match the frontend
app.register_blueprint(routes, url_prefix="/api")

# ===== OPTIONAL: Add a health check endpoint =====
@app.route("/")
def home():
    return {
        "message": "D-LOCK Backend API",
        "status": "running",
        "version": "1.0.0"
    }

@app.route("/health")
def health():
    return {"status": "healthy"}, 200

if __name__ == "__main__":
    # Run on http://127.0.0.1:5000
    app.run(debug=True, port=5000)