import pandas as pd
import re
import nltk
from nltk.tokenize import word_tokenize
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from flask import Blueprint, redirect, url_for, flash,render_template,request,jsonify
from db_config import db
from preprocessing import preprocess_texts
from models import DataSentimen, Preprocessing, DataTFIDF

preprocessing_bp = Blueprint("preprocessing", __name__)
@preprocessing_bp.route('/page_preprocessing')
def page_preprocessing():
    try:
        data = Preprocessing.query.all()
        return render_template('preprocessing.html', data=data)
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
        return render_template('preprocessing.html', data=[])


@preprocessing_bp.route('/preprocessing/proses', methods=['GET', 'POST'])
def preprocessing_data():
    if request.method == 'GET':
        return render_template("pre-processing.html")

    try:
        # Ambil data dari model DataSentimen
        data_sentimen = DataSentimen.query.with_entities(DataSentimen.teks, DataSentimen.labels).all()
        if not data_sentimen:
            flash("Tidak ada data yang tersedia untuk preprocessing.", "danger")
            return redirect(url_for('preprocessing.page_preprocessing'))

        # Ubah ke DataFrame
        teks_list = [d.teks for d in data_sentimen]
        labels_list = [d.labels for d in data_sentimen]
        df = preprocess_texts(teks_list, labels_list)  # fungsi ini harus mengembalikan kolom 'teks', 'labels', 'preprocessing_text'

        # Kosongkan tabel lama
        Preprocessing.query.delete()
        DataTFIDF.query.delete()
        db.session.commit()

        # Tambahkan data baru ke Preprocessing
        records = [
            Preprocessing(teks=row['teks'], labels=row['labels'], preprocessing_text=row['preprocessing_text'])
            for _, row in df.iterrows()
        ]
        db.session.bulk_save_objects(records)
        db.session.commit()

        flash("Preprocessing berhasil dilakukan!", "success")
        return redirect(url_for('preprocessing.page_preprocessing', status='preprocess_success'))

    except Exception as error:
        db.session.rollback()
        flash(f"Terjadi kesalahan: {error}", "danger")
        return redirect(url_for('preprocessing.page_preprocessing'))






#
# @preprocessing_bp.route('/page_preprocessing')
# def page_preprocessing():
#     connection = connect_db()
#     if not connection:
#         flash('Koneksi ke database gagal', 'error')
#         return redirect(url_for('preprocessing.page_preprocessing'))
#     try:
#         cursor = connection.cursor()
#         cursor.execute("SELECT * FROM preprocessing")
#         data = cursor.fetchall()
#         return render_template('preprocessing.html',data=data)
#     except Exception as e:
#         flash(f'Terjadi kesalahan: {str(e)}', 'error')
#         return redirect(url_for('preprocessing.page_preprocessing'))

# @preprocessing_bp.route('/preprocessing/proses', methods=['GET', 'POST'])
# def preprocessing_data():
    if request.method == 'GET':
        return render_template("pre-processing.html")
    try:
        # Ambil data dari database
        connection = connect_db()
        with connection.cursor() as cursor:
            cursor.execute("SELECT teks,labels FROM data_sentimen")
            data_sentimen = [{"teks": row[0], "labels": row[1]} for row in cursor.fetchall()]

        # Cek apakah data kosong
        if not data_sentimen:
            flash("Tidak ada data yang tersedia untuk preprocessing.", "danger")
            return redirect(url_for('preprocessing.page_preprocessing'))

        # Ubah hasil query menjadi DataFrame
        df = pd.DataFrame(data_sentimen, columns=["teks","labels"])
        teks_list = [item['teks'] for item in data_sentimen]
        labels_list = [item['labels'] for item in data_sentimen]
        df = preprocess_texts(teks_list, labels_list)

        # Simpan hasil ke database
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE preprocessing")
            cursor.executemany(
                """
                INSERT INTO preprocessing (teks, labels, preprocessing_text)
                VALUES (%s, %s, %s)
                """,
                df[['teks', 'labels', 'preprocessing_text']].values.tolist()
            )

            # Hapus duplikat dalam tabel preprocessing
            cursor.execute("""
                DELETE FROM preprocessing
                WHERE id NOT IN (
                    SELECT MIN(id) FROM preprocessing GROUP BY teks
                )
            """)
            # hapus data yang ada pada tabel
            cursor.execute("TRUNCATE TABLE data_tfidf")
            connection.commit()

        connection.close()
        flash("Preprocessing berhasil dilakukan!", "success")
        return redirect(url_for('preprocessing.page_preprocessing', status='preprocess_success'))

    except Exception as error:
        flash(f"Terjadi kesalahan: {error}", "danger")
        return redirect(url_for('preprocessing.page_preprocessing'))
