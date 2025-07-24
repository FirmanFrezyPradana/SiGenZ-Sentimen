
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from routes import register_blueprints  # Ambil fungsi dari routes/__init__.py
from db_config import db

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

# Konfigurasi SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
    f"@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Registrasi semua Blueprint
register_blueprints(app)

@app.route('/')
def index():
    try:
        return render_template('dashboard.html')
    except Exception as e:
        return f"❌ Gagal terhubung ke MySQL: {str(e)}"

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='127.0.0.1', port=3000, debug=True)

