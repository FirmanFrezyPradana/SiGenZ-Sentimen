import pandas as pd
import numpy as np
from flask import Blueprint, jsonify,render_template, flash,request
from db_config import db
## manual
# from tfidf import compute_tfidf,compute_idf,saveTFIDF
## library
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy import text
from sklearn.model_selection import train_test_split
from models import DataTraining,DataTesting, Preprocessing, DataTFIDF
import pickle

pembobotan_bp = Blueprint('pembobotan', __name__)
@pembobotan_bp.route('/pembobotan')
def page_tfidf():
    try:
        data = DataTFIDF.query.all()
        return render_template('tfidf.html', data=data)
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
        return render_template('tfidf.html', data=[])

@pembobotan_bp.route('/proses-tfidf', methods=['POST'])
def proses_tfidf():
    try:
        # ========================================== ambil data dari tabel ================================================
        data_preprocessing = Preprocessing.query.all()
        db.session.execute(text("TRUNCATE TABLE data_tfidf"))
        db.session.execute(text("TRUNCATE TABLE klasifikasiTestingModel"))
        if not data_preprocessing:
            return jsonify({'status': 'error', 'message': 'Tidak ada data pada preprocessing yang tersedia.'})

        # menyiapkan daftar teks asli, teks hasil preprocessing, dan label dari dataset
        teks = [row.teks for row in data_preprocessing]
        preprocessing_texts = [row.preprocessing_text for row in data_preprocessing]
        labels = [row.labels for row in data_preprocessing]

        # ========================================== start manual ================================================
        # hitung tf-idf dan hitung idf asli (dictionary)
        # tfidf_df = compute_tfidf(preprocessing_texts)
        # idf = compute_idf(preprocessing_texts)
        # saveTFIDF(tfidf_df, idf)
        # tfidf_matrix = tfidf_df.to_numpy()
        # ========================================== end manual ================================================

        # ========================================== start pembobotan ================================================
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(preprocessing_texts)

        # Simpan ke file
        with open('static/model/tfidf_vectorizer.pkl', 'wb') as tfidf_vectorizer_file:
            pickle.dump(vectorizer, tfidf_vectorizer_file)

        # Konversi hasilnya ke DataFrame
        df_tfidf = pd.DataFrame(
            tfidf_matrix.toarray(),
            columns=vectorizer.get_feature_names_out()
        )
        tfidf_matrix = df_tfidf.to_numpy()
        # ========================================== end pembobotan ================================================

        # ========================================== start input database ================================================
        for i in range(len(data_preprocessing)):
            tfidf_json = ",".join([str(round(val, 6)) for val in tfidf_matrix[i].tolist()])
            data_tfidf = DataTFIDF(
                teks=teks[i],
                preprocessing_text=preprocessing_texts[i],
                labels=labels[i],
                tfidf=tfidf_json
            )
            db.session.add(data_tfidf)
        db.session.commit()
        db.session.execute(text("TRUNCATE TABLE data_testing"))
        db.session.execute(text("TRUNCATE TABLE data_training"))

        # ========================================== split data ================================================
        split_data()
        # ========================================== redirect succses ================================================
        return jsonify({'status': 'success'})

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': {str(error)}})

def split_data():
    try:
        split_ratio = request.json.get('split_ratio', 0.8)
        data = DataTFIDF.query.all()
        if not data:
            return jsonify({'status': 'error', 'message': 'Tidak ada data. Tidak dapat melakukan split.'})

        df = pd.DataFrame([{
            'teks': d.teks,
            'preprocessing_text': d.preprocessing_text,
            'labels': d.labels,
            'tfidf': d.tfidf
        } for d in data])

        test_size = 1.0 - float(split_ratio)

        # Split data
        train_data, test_data = train_test_split(df, test_size=test_size, random_state=42)

        for _, row in train_data.iterrows():
            db.session.add(DataTraining(
                teks=row['teks'],
                preprocessing_text=row['preprocessing_text'],
                labels=row['labels'],
                tfidf=row['tfidf']
            ))

        for _, row in test_data.iterrows():
            db.session.add(DataTesting(
                teks=row['teks'],
                preprocessing_text=row['preprocessing_text'],
                labels=row['labels'],
                tfidf=row['tfidf']
            ))

        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(error)})