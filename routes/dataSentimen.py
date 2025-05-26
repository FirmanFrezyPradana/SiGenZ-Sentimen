
from flask import Blueprint, request, redirect, url_for, render_template, flash,jsonify
from models import DataSentimen
from db_config import db
from sqlalchemy import text
import pandas as pd

dataSentimen_bp = Blueprint('dataSentimen', __name__)

@dataSentimen_bp.route('/dataSentimen', methods=['GET'])
def dataSentimen():
    data = DataSentimen.query.all()
    return render_template('data_sentimen.html', data=data)


@dataSentimen_bp.route('/import_data', methods=['POST'])
def import_data():
    # if 'file' not in request.files:
    #     flash('File tidak ditemukan', 'error')
    #     return redirect(url_for('dataSentimen.dataSentimen'))

    # file = request.files['file']

    # if not file.filename.lower().endswith('.csv'):
    #     flash('File harus berformat CSV', 'error')
    #     return redirect(url_for('dataSentimen.dataSentimen'))

    # try:
    #     file_stream = TextIOWrapper(file.stream, encoding='utf-8')
    #     reader = csv.DictReader(file_stream)
    #     required_columns = ['teks', 'sosmed', 'labels']

    #     # Validasi kolom
    #     if not set(required_columns).issubset(reader.fieldnames):
    #         flash('Kolom "teks", "sosmed", dan "labels" harus ada.', 'error')
    #         return redirect(url_for('dataSentimen.dataSentimen'))

    #     # Ambil semua teks yang sudah ada di DB untuk menghindari duplikasi
    #     existing_teks = set(row[0] for row in db.session.query(DataSentimen.teks).all())

    #     new_data = []
    #     for row in reader:
    #         teks = (row['teks'] or '').strip().strip('"')
    #         sosmed = (row['sosmed'] or '').strip()
    #         labels = (row['labels'] or '').strip()

    #         if teks and teks not in existing_teks:
    #             new_data.append(DataSentimen(teks=teks, sosmed=sosmed, labels=labels))

    #     if new_data:
    #         db.session.bulk_save_objects(new_data)
    #         db.session.commit()
    #         flash(f'Berhasil menambahkan {len(new_data)} data baru.', 'success')
    #     else:
    #         flash('Semua data sudah ada atau kosong.', 'warning')

    # except Exception as e:
    #     db.session.rollback()
    #     flash(f'Terjadi kesalahan saat mengimpor: {str(e)}', 'error')

    if request.method == "POST" and "file" in request.files:
            file = request.files["file"]

            if file and file.filename.endswith(".csv"):
                try:
                    df = pd.read_csv(file)

                    # Validasi kolom wajib
                    required_columns = {'teks', 'sosmed', 'labels'}
                    if not required_columns.issubset(df.columns):
                        flash('Kolom "teks", "sosmed", dan "labels" harus ada.', 'danger')
                        return redirect(url_for('dataSentimen.dataSentimen'))

                    # Ambil semua teks yang sudah ada di database
                    existing_teks = set(row[0] for row in db.session.query(DataSentimen.teks).all())

                    new_data = []
                    for _, row in df.iterrows():
                        teks = (str(row.get('teks', '')).strip().strip('"'))
                        sosmed = (str(row.get('sosmed', '')).strip())
                        labels = (str(row.get('labels', '')).strip())

                        if teks and teks not in existing_teks:
                            new_data.append(DataSentimen(teks=teks, sosmed=sosmed, labels=labels))

                    if new_data:
                        db.session.bulk_save_objects(new_data)
                        db.session.commit()
                        flash(f'Berhasil menambahkan {len(new_data)} data baru.', 'success')
                    else:
                        flash('Semua data sudah ada atau kosong.', 'warning')

                except Exception as e:
                    db.session.rollback()
                    flash(f'Gagal mengimpor data: {str(e)}', 'danger')

            else:
                flash('File harus berupa CSV.', 'warning')

    return redirect(url_for('dataSentimen.dataSentimen', status='import_success'))


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
