from flask import Blueprint, redirect, url_for, flash,render_template, jsonify, request
from db_config import db
from preprocessing import preprocess_texts
from models import DataSentimen, Preprocessing
from sqlalchemy import text

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
            return jsonify({'status': 'error', 'message': 'Tidak ada data yang tersedia untuk preprocessing.'})

        # Ubah ke DataFrame
        teks_list = [d.teks for d in data_sentimen]
        labels_list = [d.labels for d in data_sentimen]
        df = preprocess_texts(teks_list, labels_list)  # fungsi ini harus mengembalikan kolom 'teks', 'labels', 'preprocessing_text'

        # Kosongkan tabel lama
        db.session.execute(text("TRUNCATE TABLE preprocessing"))
        db.session.execute(text("TRUNCATE TABLE data_tfidf"))
        db.session.commit()

        records = [
            Preprocessing(teks=row['teks'], labels=row['labels'], preprocessing_text=row['preprocessing_text'])
            for _, row in df.iterrows()
        ]
        db.session.bulk_save_objects(records)
        db.session.commit()

        return jsonify({'status': 'success'})

    except Exception as error:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(error)})