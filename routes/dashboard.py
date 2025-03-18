from flask import Blueprint, render_template, flash, redirect, url_for
from db_config import connect_db

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')

@dashboard_bp.route('/')
def dashboard():
    connection = connect_db()
    if not connection:
        flash('Koneksi ke database gagal', 'error')
        return redirect(url_for('dashboard.dashboard'))

    try:
        with connection.cursor() as cursor:

            cursor.execute("SELECT COUNT(*) FROM data_sentimen")
            jumlah_total = cursor.fetchone()[0]

            # Jumlah data sentimen positif
            cursor.execute("SELECT COUNT(*) FROM data_sentimen WHERE labels = 'positif'")
            jumlah_positif = cursor.fetchone()[0] or 0

            # Jumlah data sentimen negatif
            cursor.execute("SELECT COUNT(*) FROM data_sentimen WHERE labels = 'negatif'")
            jumlah_negatif = cursor.fetchone()[0] or 0

    except Exception as e:
        flash(f'Error saat mengambil data: {str(e)}', 'error')
        jumlah_total = 0

    return render_template("dashboard.html", jumlah_total=jumlah_total,jumlah_positif=jumlah_positif,jumlah_negatif=jumlah_negatif)




# @dashboard_bp.route('/preprocessingTrainingSentimen')
# def preprocesTrainSentimen():
#     return render_template('data_training_preprocessing.html')
