
from flask import Blueprint, request, redirect, url_for, render_template, flash
from models import DataSentimen
from db_config import db
from sqlalchemy import text

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

@dataSentimen_bp.route('/dataSentimen/reset_all', methods=['POST'])
def reset_all_data():
    try:
        db.session.execute(text("TRUNCATE TABLE data_sentimen"))
        db.session.execute(text("TRUNCATE TABLE data_training"))
        db.session.execute(text("TRUNCATE TABLE data_testing"))
        db.session.execute(text("TRUNCATE TABLE preprocessing"))
        db.session.execute(text("TRUNCATE TABLE data_tfidf"))
        db.session.execute(text("TRUNCATE TABLE klasifikasiTestingModel"))
        db.session.commit()
        flash('Seluruh data pada tabel preprocessing dan data_tfidf berhasil dihapus!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
    return redirect(url_for('dataSentimen.dataSentimen'))
