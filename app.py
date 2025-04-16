from flask import Flask, render_template
import os
from routes.dashboard import dashboard_bp
from routes.dataSentimen import dataSentimen_bp
from routes.dataTraining import dataTraining_bp
from routes.preprocessing import preprocessing_bp
from routes.importData import import_bp
from routes.pembobotan import pembobotan_bp
from db_config import connect_db

app = Flask(__name__)

app.secret_key = os.urandom(24)
# Register Blueprint setelah konfigurasi database
app.register_blueprint(dashboard_bp)
app.register_blueprint(dataSentimen_bp)
app.register_blueprint(dataTraining_bp)
app.register_blueprint(preprocessing_bp)
app.register_blueprint(import_bp)
app.register_blueprint(pembobotan_bp)

@app.route('/')
def index():
    connection = connect_db()
    if connection and connection.is_connected():
        connection.close()
        return render_template('dashboard.html')
    return "❌ Gagal terhubung ke MySQL."

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(debug=True)
