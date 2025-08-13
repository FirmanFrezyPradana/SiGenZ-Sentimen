from flask import Blueprint, flash,render_template,request,redirect,url_for,jsonify
import pandas as pd
from db_config import db
from preprocessing import preprocess_texts
import pickle
from models import testingModel
from sqlalchemy import text

testing_bp = Blueprint("testing", __name__)
@testing_bp.route('/hal_testing')
def page_testing():
    data = testingModel.query.all()
    jumlah_positif = testingModel.query.filter(testingModel.label_prediksi == 'positif').count()
    jumlah_negatif = testingModel.query.filter(testingModel.label_prediksi == 'negatif').count()
    jumlah_total = testingModel.query.count()
    return render_template('testing.html',data=data,jumlah_positif=jumlah_positif,jumlah_negatif=jumlah_negatif,jumlah_total=jumlah_total)

@testing_bp.route('/import_data_testing', methods=['POST'])
def upload_testing():
    if request.method == "POST" and "file" in request.files:
        file = request.files["file"]
        if file and file.filename.endswith(".csv"):
            try:
                df = pd.read_csv(file)
                # Validasi kolom 'teks' atau 'Comment'
                if not ('teks' in df.columns or 'Comment' in df.columns):
                    return jsonify({'error': 'Kolom "teks" atau "Comment" harus ada di file.'})
                # Ambil kolom teks
                df['teks'] = df['teks'] if 'teks' in df.columns else df['Comment']

                # Preprocessing
                teks_list = df['teks'].astype(str).tolist()

                df_preprocessed = preprocess_texts(teks_list)
                df['preprocessed_text'] = df_preprocessed['preprocessing_text']


                # Load TF-IDF
                with open('static/model/tfidf_vectorizer.pkl', 'rb') as tfidf_vectorizer_file:
                    vectorizer = pickle.load(tfidf_vectorizer_file)
                X_transformed = vectorizer.transform(df['preprocessed_text'])

                # Load model SVM
                with open('static/model/model_svm_linear.pkl', 'rb') as model_file:
                    model = pickle.load(model_file)
                prediksi = model.predict(X_transformed)
                df['hasil'] = prediksi
                db.session.execute(text("TRUNCATE TABLE testing"))
                # Simpan ke DB
                for _, row in df.iterrows():
                    hasil = "Negatif" if row['hasil'] == -1 else "Positif"
                    data = testingModel(
                        teks=row['teks'],
                        preprocessing=row['preprocessed_text'],
                        label_prediksi=hasil
                    )
                    db.session.add(data)
                db.session.commit()

                return redirect(url_for('testing.page_testing'))

            except Exception as e:
                return jsonify({'error': f'Error: {str(e)}'})
        else:
            return jsonify({'error': 'File harus berformat CSV'})
    else:
        return jsonify({'error': 'Metode HTTP tidak valid, hanya mendukung POST'})
