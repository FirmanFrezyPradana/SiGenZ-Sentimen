from tfidf import transform
from flask import Blueprint
from flask import jsonify
import pickle
from preprocessing import preprocess_texts

cek_bp = Blueprint('cek', __name__)

@cek_bp.route('/cek', methods=['GET'])
def cek():
    # kalimat uji dan preprocessing
    kalimat_baru = ["semoga genz sukses"]
    df = preprocess_texts(kalimat_baru)
    # karena hanya mengambil 1 baris makan gunakan .iloc[0]
    teks_baru = df['preprocessing_text'].iloc[0]

    # menangani teks yang berupa list
    if isinstance(teks_baru, list):
        teks_baru = ' '.join(teks_baru)

    # transformasi  pembobotan tfidf
    hasil_tfidf = transform(teks_baru)
    hasil_tfidf = [hasil_tfidf]

    # memuat model svm
    with open('static/model/model_svm_linear.pkl', 'rb') as model_file:
        loaded_linear_model = pickle.load(model_file)
    # prediksi
    hasil_linear = loaded_linear_model.predict(hasil_tfidf)
    label_prediksi = "Positif" if hasil_linear[0] == 1 else "Negatif"

    return jsonify({
        'teks_preprocessing': teks_baru,
        'prediksi': label_prediksi,
    })

