# from flask import Blueprint, request, jsonify,redirect, url_for,render_template, flash
# from db_config import connect_db

# dataSentimen_bp = Blueprint('dataSentimen', __name__)

# @dataSentimen_bp.route('/dataSentimen', methods=['GET', 'POST'])
# def dataSentimen():
#     connection = connect_db()
#     if not connection:
#         flash('Koneksi ke database gagal', 'error')
#         return redirect(url_for('dataSentimen.dataSentimen'))

#     try:
#         cursor = connection.cursor()

#         if request.method == 'POST':
#             teks = request.form.get('teks')
#             sosmed = request.form.get('sosmed')
#             labels = request.form.get('labels')

#             if not teks or not sosmed or not labels:
#                 flash('Semua kolom harus diisi', 'error')
#                 return redirect(url_for('dataSentimen.dataSentimen'))

#             query = "INSERT INTO data_sentimen (teks, sosmed, labels) VALUES (%s, %s, %s)"
#             cursor.execute(query, (teks, sosmed, labels))
#             connection.commit()
#             flash('Data berhasil ditambahkan!', 'success')
#             return redirect(url_for('dataSentimen.dataSentimen',status='Upload_success'))

#         # Jika request adalah GET (ambil data)
#         cursor.execute("SELECT teks, sosmed, labels FROM data_sentimen")
#         data = cursor.fetchall()
#         return render_template('data_sentimen.html', data=data)

#     except Exception as e:
#         flash(f'Terjadi kesalahan: {str(e)}', 'error')
#         return redirect(url_for('dataSentimen.dataSentimen'))

# @dataSentimen_bp.route('/dataSentimen/Delete_all', methods=['POST'])
# def delete_all_data():
#     connection = connect_db()
#     if not connection:
#         flash('Koneksi ke database gagal', 'error')
#         return redirect(url_for('dataSentimen.dataSentimen'))

#     try:
#         cursor = connection.cursor()
#         cursor.execute("TRUNCATE TABLE data_sentimen")  # Menghapus semua data
#         connection.commit()
#         flash('Semua data berhasil dihapus!', 'success')
#     except Exception as e:
#         flash(f'Terjadi kesalahan: {str(e)}', 'error')
#     finally:
#         cursor.close()
#         connection.close()

#     return redirect(url_for('dataSentimen.dataSentimen'))  # Redirect untuk merefresh tampilan

from flask import Blueprint, request, jsonify, redirect, url_for, render_template, flash
from models import DataSentimen
from db_config import db

dataSentimen_bp = Blueprint('dataSentimen', __name__)

@dataSentimen_bp.route('/dataSentimen', methods=['GET', 'POST'])
def dataSentimen():
    if request.method == 'POST':
        teks = request.form.get('teks')
        sosmed = request.form.get('sosmed')
        labels = request.form.get('labels')

        if not teks or not sosmed or not labels:
            flash('Semua kolom harus diisi', 'error')
            return redirect(url_for('dataSentimen.dataSentimen'))

        try:
            data = DataSentimen(teks=teks, sosmed=sosmed, labels=labels)
            db.session.add(data)
            db.session.commit()
            flash('Data berhasil ditambahkan!', 'success')
            return redirect(url_for('dataSentimen.dataSentimen', status='Upload_success'))
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal menyimpan data: {str(e)}', 'error')
            return redirect(url_for('dataSentimen.dataSentimen'))

    # Jika GET
    data = DataSentimen.query.all()
    return render_template('data_sentimen.html', data=data)

@dataSentimen_bp.route('/dataSentimen/Delete_all', methods=['POST'])
def delete_all_data():
    try:
        delete = db.session.query(DataSentimen).delete()
        db.session.commit()
        flash(f'{delete} data berhasil dihapus!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan: {str(e)}', 'error')

    return redirect(url_for('dataSentimen.dataSentimen'))
