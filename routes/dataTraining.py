from flask import Blueprint, request, jsonify,redirect, url_for,render_template, flash
from db_config import connect_db

dataTraining_bp = Blueprint('dataTraining', __name__)

@dataTraining_bp.route('/hal_DataTraining',methods=['GET'])
def dataTraining():
    connection = connect_db()
    if not connection:
        flash('Koneksi ke database gagal', 'error')
        return redirect(url_for('dataTraining.dataTraining'))

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM data_training")
        data = cursor.fetchall()
        return render_template('data_training.html', data=data)

    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
        return redirect(url_for('dataTraining.dataTraining'))