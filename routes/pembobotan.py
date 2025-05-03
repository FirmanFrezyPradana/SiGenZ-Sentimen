import pandas as pd
import numpy as np
from flask import Blueprint, request, jsonify, redirect, url_for, render_template, flash
from db_config import db
from tfidf import compute_tfidf
from sklearn.model_selection import train_test_split
from models import DataTraining,DataTesting, Preprocessing, DataTFIDF

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
        data_preprocessing = Preprocessing.query.all()
        if not data_preprocessing:
            flash ("tidak ada data pada preprocessing yang trsedia .","danger")
            return redirect(url_for('pembobotan.page_tfidf'))

        teks = [row.teks for row in data_preprocessing]
        preprocessing_texts = [row.preprocessing_text for row in data_preprocessing]
        labels = [row.labels for row in data_preprocessing]

        # hitung tf-idf
        df = pd.DataFrame({
            "teks": teks,
            "preprocessing_text": preprocessing_texts,
            "labels": labels
        })
        tfidf_df = compute_tfidf(preprocessing_texts)
        tfidf_matrix = tfidf_df.to_numpy()

        for i in range(len(data_preprocessing)):
            if not DataTFIDF.query.filter_by(preprocessing_text=preprocessing_texts[i]).first():
                tfidf_json = ",".join([str(round(val, 6)) for val in tfidf_matrix[i].tolist()])
                new_row = DataTFIDF(
                    teks=teks[i],
                    preprocessing_text=preprocessing_texts[i],
                    labels=labels[i],
                    tfidf=tfidf_json
                )
                db.session.add(new_row)

        db.session.commit()
        split_data()
        flash('Data TF-IDF berhasil disimpan!','success')
        return redirect(url_for('pembobotan.page_tfidf'))

    except Exception as error:
        db.session.rollback()
        flash(f"Terjadi kesalahan :{error}","danger")
        return jsonify({'error':str(KeyError)})

def split_data():
    try:
        data = DataTFIDF.query.all()
        if not data:
            flash("Data TF-IDF kosong. Tidak dapat melakukan split.", "warning")
            return

        df = pd.DataFrame([{
            'teks': d.teks,
            'preprocessing_text': d.preprocessing_text,
            'labels': d.labels,
            'tfidf': d.tfidf
        } for d in data])

        # Split data
        train_data, test_data = train_test_split(df, test_size=0.2, random_state=42)

        db.session.query(DataTraining).delete()
        db.session.query(DataTesting).delete()

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
        flash(f"Data berhasil di-split dan disimpan ke data_training dan data_testing","succes")
    except Exception as error:
        db.session.rollback()
        flash(f"Terjadi kesalahan saat split data: {error}", "danger")
    # connection = connect_db()
    # try:
    #     with connection.cursor() as cursor:
    #         # Ambil data teks dan label dari tabel preprocessing
    #         cursor.execute("SELECT teks,preprocessing_text, labels FROM preprocessing")
    #         data = cursor.fetchall()
    #     # Pisahkan teks dan label
    #     df = pd.DataFrame(data, columns=['teks','preprocessing_text', 'labels'])
    #     text =df['teks'].tolist()
    #     documents = df['preprocessing_text'].tolist()
    #     labels = df['labels'].tolist()
    #     tfidf_df = compute_tfidf(documents)
    #     X = tfidf_df.to_numpy()

    #     # Simpan hasil ke dalam tabel data_tfidf
    #     with connection.cursor() as cursor:
    #         for i in range(len(documents)):
    #             preprocessing_text = documents[i]
    #             teks = text[i]
    #             label = labels[i]
    #             tfidf_vector = X[i].tolist()  # ambil vektor TF-IDF
    #             tfidf_json = ",".join([str(round(val, 6)) for val in tfidf_vector])  # ubah ke format "[0.324234,0.0,..]" menjadi "0.324234,0.0,.."

    #             # Cek apakah terdapat duplikasi pada tabel
    #             cursor.execute("SELECT COUNT(*) FROM data_tfidf WHERE preprocessing_text = %s", (preprocessing_text,))
    #             exists = cursor.fetchone()[0]
    #             if exists == 0:
    #                  cursor.execute("""
    #                     INSERT INTO data_tfidf (teks,preprocessing_text, labels, tfidf)
    #                         VALUES (%s,%s, %s, %s)
    #                     """, (teks,preprocessing_text, label, tfidf_json))

    #     split_data(connection)
    #     connection.commit()
    #     flash('Data berhasil ditambahkan!', 'success')
    #     return redirect(url_for('pembobotan.page_tfidf', status='preprocess_success'))

    # except Exception as error:
    #     connection.rollback()
    #     flash(f"Terjadi kesalahan: {error}", "danger")
    #     # return redirect(url_for('preprocessing.page_preprocessing'))
    #     return jsonify({'error': str(error)})
    # finally:
    #     connection.close()

#     # end database
# def split_data(connection):
#     cursor = connection.cursor()
#     try:
#         cursor.execute("SELECT teks, preprocessing_text, labels, tfidf FROM data_tfidf")
#         data = cursor.fetchall()

#         # Membuat DataFrame
#         df = pd.DataFrame(data, columns=['teks', 'preprocessing_text', 'labels', 'tfidf'])

#         # Melakukan split data
#         train_data, test_data = train_test_split(df, test_size=0.2, random_state=42)

#         cursor.execute("DELETE FROM data_training")
#         cursor.execute("DELETE FROM data_testing")

#         # Menyimpan data training ke tabel data_training
#         for _, row in train_data.iterrows():
#             sql_train = """
#                 INSERT INTO data_training (teks, preprocessing_text, labels, tfidf)
#                 VALUES (%s, %s, %s, %s)
#             """
#             cursor.execute(sql_train, (row['teks'], row['preprocessing_text'], row['labels'], row['tfidf']))

#         # Menyimpan data testing ke tabel data_testing
#         for _, row in test_data.iterrows():
#             sql_test = """
#                 INSERT INTO data_testing (teks, preprocessing_text, labels, tfidf)
#                 VALUES (%s, %s, %s, %s)
#             """
#             cursor.execute(sql_test, (row['teks'], row['preprocessing_text'], row['labels'], row['tfidf']))

#         connection.commit()
#         return "Data success di split"
#     except Exception as error:
#         connection.rollback()
#         flash(f"Terjadi kesalahan split data: {error}", "danger")
#         # return redirect(url_for('preprocessing.page_preprocessing'))
#         return jsonify({'error': str(error)})
