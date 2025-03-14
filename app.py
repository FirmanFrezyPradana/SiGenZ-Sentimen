from flask import Flask, render_template
from routes.dashboard import dashboard_bp

app = Flask(__name__)
app.register_blueprint(dashboard_bp)

@app.route('/')  # Menampilkan dashboard.html di halaman utama
def home():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
