import csv
from io import TextIOWrapper
from flask import Blueprint, request,redirect, url_for, flash
from db_config import connect_db

import_bp = Blueprint('importData', __name__)

@import_bp.route('/import', methods=['POST'])
def import_csv():
    connection = connect_db()
    if not connection:
        flash('Koneksi ke database gagal', 'error')
        return redirect(url_for('dataSentimen.dataSentimen'))
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
        if set(reader.fieldnames) - {'no'}!= set(required_columns):
            flash('Format CSV tidak valid. Hanya kolom "teks", "sosmed", dan "labels" yang diperbolehkan', 'error')
            return redirect(url_for('dataSentimen.dataSentimen'))
        cursor = connection.cursor()
        for row in reader:
            teks = (row['teks'] or "").strip().strip('"')

            # Pastikan data tidak kosong setelah diproses
            if teks :
                query = "INSERT INTO data_sentimen (teks, sosmed, labels) VALUES (%s, %s, %s)"
                values = (teks, row['sosmed'], row['labels'])
                cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
         # Flash success message
        flash('File berhasil diunggah dan data berhasil dimasukkan.', 'success')
        return redirect(url_for('dataSentimen.dataSentimen'))   # Kembali ke halaman import.html
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
        return redirect(url_for('dataSentimen.dataSentimen'))

