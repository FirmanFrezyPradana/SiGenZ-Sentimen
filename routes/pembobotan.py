import pandas as pd
import numpy as np
import math
from flask import Blueprint, request, jsonify, redirect, url_for, render_template, flash
from db_config import connect_db

pembobotan_bp = Blueprint('pembobotan', __name__)

@pembobotan_bp.route('/pembobotan')
def page_tfidf():
    connection = connect_db()
    if not connection:
        flash('Koneksi ke database gagal', 'error')
        return redirect(url_for('pembobotan.page_tfidf'))
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM data_tfidf")
        data = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('tfidf.html', data=data)

    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
        if  connection:
            connection.close()
        return render_template('tfidf.html', data=[])

@pembobotan_bp.route('/proses-tfidf', methods=['POST'])
def proses_tfidf():
    # source code memasukkan ke database
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            # Ambil data teks dan label dari tabel preprocessing
            cursor.execute("SELECT preprocessing_text, labels FROM preprocessing")
            data = cursor.fetchall()
        # Pisahkan teks dan label
        df = pd.DataFrame(data, columns=['preprocessing_text', 'labels'])
        documents = df['preprocessing_text'].tolist()
        labels = df['labels'].tolist()

        # Hitung TF, IDF, TF-IDF
        tf = compute_tf(documents)
        idf = compute_idf(documents)
        tfidf_df = compute_tfidf(documents)

        X = tfidf_df.to_numpy()

        # Simpan hasil ke dalam tabel data_tfidf
        with connection.cursor() as cursor:
            for i in range(len(documents)):
                preprocessing_text = documents[i]
                label = labels[i]
                tfidf_vector = X[i].tolist()  # ambil vektor TF-IDF
                tfidf_json = ",".join([str(round(val, 6)) for val in tfidf_vector])  # ubah ke format "[0.324234,0.0,..]" menjadi "0.324234,0.0,.."

                 # Cek apakah terdapat duplikasi pada tabel
                cursor.execute("SELECT COUNT(*) FROM data_tfidf WHERE preprocessing_text = %s", (preprocessing_text,))
                exists = cursor.fetchone()[0]

                if exists == 0:
                    cursor.execute("""
                        INSERT INTO data_tfidf (preprocessing_text, labels, tfidf)
                        VALUES (%s, %s, %s)
                    """, (preprocessing_text, label, tfidf_json))

        connection.commit()
        flash('Data berhasil ditambahkan!', 'success')
        return redirect(url_for('pembobotan.page_tfidf', status='preprocess_success'))

    except Exception as error:
        connection.rollback()
        flash(f"Terjadi kesalahan: {error}", "danger")
        # return redirect(url_for('preprocessing.page_preprocessing'))
        return jsonify({'error': str(error)})
    finally:
        connection.close()
    # end database

# Menghitungg TF
from collections import defaultdict
def compute_tf(documents):
    ## sama seperti jurnal
    tf_list = []
    for doc in documents:
        tf_counts = defaultdict(int)
        words = doc.split()
        # Hitung frekuensi setiap kata dalam dokumen
        for word in words:
            tf_counts[word] += 1
        # Hitung TF dengan skala logaritmik: TF = 1 + log10(frek)
        tf_log_scaled = {
            word: round(1 + math.log10(count), 4)
            for word, count in tf_counts.items()
        }
        tf_list.append(tf_log_scaled)
    return tf_list

# Menghitung IDF
def compute_idf(documents):
    idf = {}
    total_docs = len(documents)
    word_set = set(word for doc in documents for word in doc.split())
    for word in word_set:
        doc_count = sum(1 for doc in documents if word in doc.split())
        # Menghindari log(0) dengan pengecekan
        # idf[word] = math.log10(total_docs / (doc_count + 1))  # Menambahkan 1 untuk menghindari pembagian dengan 0
        ## menual
        idf[word] = math.log10(total_docs / doc_count)
    return idf
# Menghitung tf-idf
def compute_tfidf(documents):
    tf = compute_tf(documents)
    idf = compute_idf(documents)
    tfidf_list = []
    for doc_tf in tf:
        tfidf_doc = {word: tf_value * idf.get(word, 0) for word, tf_value in doc_tf.items()}
        tfidf_list.append(tfidf_doc)
    # Konversi ke DataFrame dan isi nilai NaN dengan 0
    tfidf_df = pd.DataFrame(tfidf_list).fillna(0)
    return tfidf_df
# end percobaan