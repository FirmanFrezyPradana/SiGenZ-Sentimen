from flask import Blueprint, request, jsonify,redirect, url_for,render_template, flash
from db_config import db
from models import DataTesting
dataTesting_bp = Blueprint('dataTesting', __name__)

@dataTesting_bp.route('/hal_DataTesting',methods=['GET'])
def dataTesting():
    try:
        data = DataTesting.query.all()
        return render_template('tfidf.html', data=data)
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
        return render_template('tfidf.html', data=[])

    # connection = connect_db()
    # if not connection:
    #     flash('Koneksi ke database gagal', 'error')
    #     return redirect(url_for('dataTesting.dataTesting'))

    # try:
    #     cursor = connection.cursor()
    #     cursor.execute("SELECT * FROM data_testing")
    #     data = cursor.fetchall()
    #     return render_template('data_testing.html', data=data)

    # except Exception as e:
    #     flash(f'Terjadi kesalahan: {str(e)}', 'error')
    #     return redirect(url_for('dataTesting.dataTesting'))