from flask import Blueprint, render_template

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')

@dashboard_bp.route('/')  # Menampilkan dashboard.html di halaman utama
@dashboard_bp.route('/dashboard')  # Masih bisa diakses melalui /dashboard juga
def dashboard():
    return render_template('dashboard.html')
