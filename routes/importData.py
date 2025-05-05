import csv
from io import TextIOWrapper
from flask import Blueprint, request,redirect, url_for, flash
from db_config import db
from models import DataSentimen

import_bp = Blueprint('importData', __name__)

@import_bp.route('/import', methods=['POST'])
def import_csv():
    if 'file' not in request.files:
        flash('Tidak ada file yang dipilih atau file kosong', 'error')
        return redirect(url_for('dataSentimen.dataSentimen'))

    file = request.files['file']

    if not file.filename.lower().endswith('.csv'):
        flash('File yang diunggah harus berformat CSV', 'error')
        return redirect(url_for('dataSentimen.dataSentimen'))

    try:
        file_stream = TextIOWrapper(file.stream, encoding='utf-8')
        reader = csv.DictReader(file_stream)
        required_columns = ['teks', 'sosmed', 'labels']

        # Pastikan file CSV memiliki kolom yang tepat
        if set(reader.fieldnames) - {'no'} != set(required_columns):
            flash('Format CSV tidak valid. Hanya kolom "teks", "sosmed", dan "labels" yang diperbolehkan', 'error')
            return redirect(url_for('dataSentimen.dataSentimen'))

        # Menggunakan SQLAlchemy untuk menyimpan data
        for row in reader:
            teks = (row['teks'] or "").strip().strip('"')

            # Pastikan data tidak kosong setelah diproses
            if teks:
                existing_data = DataSentimen.query.filter_by(teks=teks).first()
                if not existing_data:  # Jika tidak ada data dengan teks yang sama, simpan data baru
                    data_sentimen = DataSentimen(
                        teks=teks,
                        sosmed=row['sosmed'],
                        labels=row['labels']
                    )
                    db.session.add(data_sentimen)
        db.session.commit()  # Menyimpan perubahan ke database

        flash('File berhasil diunggah dan data berhasil dimasukkan.', 'success')
        return redirect(url_for('dataSentimen.dataSentimen'))  # Kembali ke halaman import.html

    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
        return redirect(url_for('dataSentimen.dataSentimen'))

