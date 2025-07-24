from flask import Blueprint,jsonify,redirect, url_for,render_template, flash
from models import DataTFIDF,klasifikasiTestingModel,DataTraining,DataTesting
import numpy as np
from db_config import db
from sklearn.svm import SVC
# from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report,confusion_matrix,ConfusionMatrixDisplay,accuracy_score, precision_score, recall_score, f1_score, classification_report

import pickle
from scipy.sparse import csr_matrix
import os
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
from wordcloud import WordCloud
from sqlalchemy import text

implementasiSvm_bp = Blueprint('implementasiSvm', __name__)
@implementasiSvm_bp.route('/hal_klasifikasi',methods=['GET'])
def implementasiSvm():
    try:
        # ========================================== proses training datata ================================================
        # Ambil data training dari tabel DataTraining
        data_training = DataTraining.query.all()

        # Validasi jika tidak ada data
        if not data_training:
            flash("Tidak ada data untuk pelatihan.", "error")
            return redirect(url_for('implementasiSvm.implementasiSvm'))

        X_train, y_train = [], [],

        # Konversi data TF-IDF dan label = svm light
        for item in data_training:
            try:
                tfidf_vector = list(map(float, item.tfidf.split(',')))
                X_train.append(tfidf_vector)
                y_train.append(1 if item.labels.lower() == 'positif' else -1)
            except Exception as e:
                print(f"Kesalahan parsing TF-IDF: {e}")
                continue

        # Cek apakah ada data valid
        if len(X_train) == 0:
            flash("Semua data tidak valid untuk pelatihan.", "danger")
            return "Tidak ada data valid untuk pelatihan."

        # Ubah ke array/matrix
        X_train = csr_matrix(X_train)
        y_train = np.array(y_train)

        # ========================================== testing k-fold cross validation ================================================

        # Training model SVM
        svm_model = SVC(kernel='linear', C=1.0, class_weight='balanced',random_state=0)

        model = svm_model.fit(X_train, y_train)

        # Simpan model ke file
        with open('static/model/model_svm_linear.pkl', 'wb') as model_file:
            pickle.dump(model, model_file)

        # ========================================== proses testing data ================================================
        # Kosongkan tabel klasifikasi hasil sebelumnya
        db.session.execute(text("TRUNCATE TABLE klasifikasiTestingModel"))

        # Ambil data dari tabel data_testing
        data_testing = DataTesting.query.all()

        if not data_testing:
            flash("Tidak ada data untuk pengujian.", "error")
            return redirect(url_for('implementasiSvm.implementasiSvm'))

        X_test, y_test, teks_test, prep_test = [], [], [], []

        # Siapkan data uji coba svm light
        for item in data_testing:
            try:
                tfidf_vector = list(map(float, item.tfidf.split(',')))
                X_test.append(tfidf_vector)
                y_test.append(1 if item.labels.lower() == 'positif' else -1)
                teks_test.append(item.teks)
                prep_test.append(item.preprocessing_text)
            except Exception as e:
                print(f"Kesalahan parsing TF-IDF testing: {e}")
                continue

        # Pastikan ada data
        if len(X_test) == 0:
            flash("Semua data testing tidak valid.", "danger")
            return "Tidak ada data valid untuk pengujian."

        # Ubah ke bentuk array/matrix
        X_test = csr_matrix(X_test)
        y_test = np.array(y_test)

        # Load model yang telah dilatih
        with open('static/model/model_svm_linear.pkl', 'rb') as model_file:
            model = pickle.load(model_file)

        # Lakukan prediksi
        y_pred = model.predict(X_test)

        # Simpan hasil klasifikasi ke database
        for i in range(len(y_test)):
            hasil = klasifikasiTestingModel(
                teks=teks_test[i],
                preprocessing=prep_test[i],
                label_aktual="Positif" if y_test[i] == 1 else "Negatif",
                label_prediksi="Positif" if y_pred[i] == 1 else "Negatif"
            )
            db.session.add(hasil)
        db.session.commit()
        # ========================================== hitung evaluasi model ================================================
        # Inisialisasi nilai untuk TP, TN, FP, FN
        tp = tn = fp = fn = 0


        ##Iterasi melalui semua data untuk menghitung TP, TN, FP, FN
        for i in range(len(y_test)):
            if y_test[i] == -1 and y_pred[i] == -1:  # True Negative
                tn += 1
            elif y_test[i] == 1 and y_pred[i] == 1:  # True Positive
                tp += 1
            elif y_test[i] == -1 and y_pred[i] == 1:  # False Positive
                fp += 1
            elif y_test[i] == 1 and y_pred[i] == -1:  # False Negative
                fn += 1
        # Hitung metrik evaluasi tanpa pembulatan
        accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = (2 * (precision * recall)) / (precision + recall) if (precision + recall) > 0 else 0

        report = classification_report(y_test, y_pred, output_dict=True)
        report.pop('macro avg', None)
        report.pop('weighted avg', None)
        for label, metrics in report.items():
            if isinstance(metrics, dict):
                metrics['precision'] = round(metrics['precision'] * 100, 2)
                metrics['recall'] = round(metrics['recall'] * 100, 2)
                metrics['f1_score'] = round(metrics['f1-score'] * 100, 2)
        # ========================================== evaluasi model ================================================
        cm = confusion_matrix(y_test, y_pred, labels=[1, -1])
        cm_display = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Positif", "Negatif"])
        cm_display.plot(cmap='Blues', values_format='d')

        confusion_matrix_path = os.path.join("static", "images", "confusion_matrix.png")
        plt.savefig(confusion_matrix_path)
        plt.close()

        # ========================================== worldcloud ================================================

        # ambil data dari klasifikasiTestingModel
        klasifikasi = klasifikasiTestingModel.query.all()
        # Mengambil teks untuk kelas 'positive', 'negative'
        positive_list = []
        negative_list = []
        # Iterasi data untuk memisahkan berdasarkan label
        for record in klasifikasi:
            if record.label_prediksi.lower() == 'positif':
                positive_list.append(record.preprocessing)
            elif record.label_prediksi.lower() == 'negatif':
                negative_list.append(record.preprocessing)

        # Gabungkan semua teks menjadi satu string per label
        positive_text = ' '.join(positive_list)
        negative_text = ' '.join(negative_list)

        # Membuat WordCloud untuk setiap kelas
        positive_wc = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate(positive_text)
        negative_wc = WordCloud(width=800, height=400, background_color='white', colormap='coolwarm').generate(negative_text)

        # Simpan gambar WordCloud ke static folder
        positive_wc_path = 'static/images/wordcloud_positive.png'
        negative_wc_path = 'static/images/wordcloud_negative.png'

        positive_wc.to_file(positive_wc_path)
        negative_wc.to_file(negative_wc_path)

        # Buat dictionary untuk wordcloud images
        wordcloud_images = {
            'positive': 'images/wordcloud_positive.png',
            'negative': 'images/wordcloud_negative.png',
        }
        # menampilkan klasifikasi
        klasifikasiTesting = klasifikasiTestingModel.query.all()
        jml_klas_positif = klasifikasiTestingModel.query.filter(klasifikasiTestingModel.label_prediksi == 'positif').count()
        jml_klas_negatif = klasifikasiTestingModel.query.filter(klasifikasiTestingModel.label_prediksi == 'negatif').count()

        return render_template(
        'klasifikasi.html',
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1=f1,
        wordcloud_images=wordcloud_images,
        report=report,
        klasifikasiTesting=klasifikasiTesting,
        positif_klas = jml_klas_positif,
        negatif_klas = jml_klas_negatif,
        )


    except Exception as error:
        flash(f"Terjadi kesalahan saat pelatihan SVM: {str(error)}", "danger")
        return redirect(url_for('implementasiSvm.implementasiSvm'))
