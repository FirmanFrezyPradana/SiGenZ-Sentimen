# from tfidf import transform
from flask import Blueprint
from flask import jsonify ,render_template,request
import pickle
from preprocessing import preprocess_texts

cek_bp = Blueprint('cek', __name__)

@cek_bp.route('/cek', methods=['POST','GET'])
def cek():
    label_prediksi = ''
    preprocessing_teks = ''
    teks = ''
    teks = request.form.get('teks','')
    if teks:
        df = preprocess_texts([teks])
        # karena hanya mengambil 1 baris makan gunakan .iloc[0]
        preprocessing_teks = df['preprocessing_text'].iloc[0]

        # menangani teks yang berupa list
        if isinstance(preprocessing_teks, list):
            preprocessing_teks = ' '.join(preprocessing_teks)

        # Load TF-IDF vectorizer
        with open('static/model/tfidf_vectorizer.pkl', 'rb') as vec_file:
            vectorizer = pickle.load(vec_file)

        # Transformasi teks uji ke bentuk TF-IDF
        hasil_tfidf = vectorizer.transform([preprocessing_teks])

        # Load model SVM
        with open('static/model/model_svm_linear.pkl', 'rb') as model_file:
            loaded_linear_model = pickle.load(model_file)

        # prediksi
        hasil_linear = loaded_linear_model.predict(hasil_tfidf)
        label_prediksi = "Positif" if hasil_linear[0] == 1 else "Negatif"


    return render_template('cekKalimat.html',teks=teks, preprocessing_teks=preprocessing_teks,label_prediksi=label_prediksi)

