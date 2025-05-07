# from flask import Flask, render_template
# import os
# from db_config import connect_db
# from routes import register_blueprints  # Ambil fungsi dari routes/__init__.py

# app = Flask(__name__)
# app.secret_key = os.urandom(24)

# # Registrasi semua Blueprint secara terpusat
# register_blueprints(app)

# @app.route('/')
# def index():
#     connection = connect_db()
#     if connection and connection.is_connected():
#         connection.close()
#         return render_template('dashboard.html')
#     return "❌ Gagal terhubung ke MySQL."

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from routes import register_blueprints  # Ambil fungsi dari routes/__init__.py
from db_config import db

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Konfigurasi SQLAlchemy
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1/Genz_sentimen'
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
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000, debug=True)

