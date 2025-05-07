from flask import Blueprint, request, jsonify,redirect, url_for,render_template, flash
from models import DataTFIDF,Preprocessing,klasifikasiTestingModel
import numpy as np
from db_config import db
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report,confusion_matrix,ConfusionMatrixDisplay
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
from scipy.sparse import csr_matrix
import os
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
from wordcloud import WordCloud
from sqlalchemy import text

implementasiSvm_bp = Blueprint('implementasiSvm', __name__)

# @implementasiSvm_bp.route('/hal_klasifikasi',methods=['GET'])
def hal_klasifikasi():
    try:
        return render_template('klasifikasi.html')
    except Exception as error:
        flash(f"Terjadi kesalahan saat pelatihan SVM: {str(error)}", "danger")
        return jsonify({"error": str(error)}), 500

# @implementasiSvm_bp.route('/implementasiSvm',methods=['GET','POST'])
@implementasiSvm_bp.route('/hal_klasifikasi',methods=['GET'])
def implementasiSvm():
    try:

        # preprocessingData = Preprocessing.query.all()
        # if not preprocessingData:
        #     flash("tidak ada data untuk pelatihan.", "error")
        #     return redirect(url_for('implementasiSvm.implementasiSvm'))

        # teks = [item.teks for item in preprocessingData]
        # corpus = [item.preprocessing_text for item in preprocessingData]
        # labels = [1 if item.labels == 'Positif' else -1 for item in preprocessingData]

        # # TF-IDF
        # tfidf_vectorizer = TfidfVectorizer()
        # tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)

        # # Simpan vectorizer
        # with open('tfidf_vectorizer.pkl', 'wb') as tfidf_vectorizer_file:
        #     pickle.dump(tfidf_vectorizer, tfidf_vectorizer_file)

        # # Split data
        # X_train, X_test, y_train, y_test = train_test_split(tfidf_matrix, labels, test_size=0.2, random_state=0)

        # # Latih model SVM
        # linear = SVC(kernel="linear", C=1.0, random_state=0,class_weight='balanced')
        # model = linear.fit(X_train, y_train)

        # # Prediksi
        # y_pred = model.predict(X_test)

        # # Hitung metrik evaluasi (dengan label angka, bukan string)
        # tp = sum((y_test[i] == 1) and (y_pred[i] == 1) for i in range(len(y_test)))
        # tn = sum((y_test[i] == -1) and (y_pred[i] == -1) for i in range(len(y_test)))
        # fp = sum((y_test[i] == -1) and (y_pred[i] == 1) for i in range(len(y_test)))
        # fn = sum((y_test[i] == 1) and (y_pred[i] == -1) for i in range(len(y_test)))

        # # Fungsi konversi label angka ke string
        # def interpret_label(val):
        #     return "Positif" if val == 1 else "Negatif"

        # # Data hasil klasifikasi
        # data = []
        # for i in range(len(y_test)):
        #     data.append({
        #         'label': interpret_label(y_test[i]),
        #         'prediksi': interpret_label(y_pred[i])
        #     })

        # # Hitung metrik
        # accuracy = round((tp + tn) / (tp + tn + fp + fn), 4) if (tp + tn + fp + fn) > 0 else 0
        # precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0
        # recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0

        # # Response JSON
        # return jsonify({
        #     'accuracy': f"{accuracy * 100:.2f}%",
        #     'precision': f"{precision * 100:.2f}%",
        #     'recall': f"{recall * 100:.2f}%",
        #     'true_positive': int(tp),
        #     'true_negative': int(tn),
        #     'false_positive': int(fp),
        #     'false_negative': int(fn),
        #     'jumlah_data': int(len(y_test)),
        #     # 'data_klasifikasi': data
        # })


        # # metode tfidf manual
        # ========================================== ambil data TF-IDF ================================================
        data_tfidf = DataTFIDF.query.all()
        db.session.execute(text("TRUNCATE TABLE klasifikasiTestingModel"))
        if not data_tfidf:
            flash("tidak ada data untuk pelatihan.","error")
            return redirect(url_for('implementasiSvm.implementasiSvm'))
        X,y,teks = [],[],[]
        for record in data_tfidf:
            try:
                tfidf_vector = list(map(float, record.tfidf.split(',')))
                X.append(tfidf_vector)
                y.append(1 if record.labels == 'Positif' else -1)
                teks.append(record.teks)
            except Exception as e:
                print(f"Kesalahan parsing TF-IDF: {e}")
                continue
        if len(X) == 0:
            flash("Semua data tidak valid untuk pelatihan.", "danger")
            # return redirect(url_for('implementasiSvm.implementasiSvm'))
            return "error"
        # ========================================== implementasi metode svm ================================================
        X = csr_matrix(X)
        y = np.array(y)
        teks = np.array(teks)
        X_train, X_test, y_train, y_test, teks_train, teks_test = train_test_split(X, y, teks, test_size=0.2, random_state=42)
        svm_model = SVC(kernel='linear',C=1.0,class_weight='balanced')
        model = svm_model.fit(X_train,y_train)
        # Menyimpan model SVM linear ke dalam file
        svm_vectorizer_path = 'static/models/svm_linear_model.pkl'
        with open(svm_vectorizer_path, 'wb') as model_file:
            pickle.dump(model, model_file)
        # ========================================== evaluasi model ================================================
        y_pred = model.predict(X_test)
        for i in range(len(y_test)):
            data = klasifikasiTestingModel(
                teks=teks_test[i],
                label_aktual="Positif" if y_test[i] == 1 else "Negatif",
                label_prediksi="Positif" if y_pred[i] == 1 else "Negatif"
            )
            db.session.add(data)
        db.session.commit()
        klasifikasiTesting = klasifikasiTestingModel.query.all()

        # Hitung metrik evaluasi secara manual (dengan label angka, bukan string)
        # Inisialisasi nilai untuk TP, TN, FP, FN
        tp = tn = fp = fn = 0
        # data = []

        # Iterasi melalui semua data untuk menghitung TP, TN, FP, FN
        for i in range(len(y_test)):
            if y_test[i] == -1 and y_pred[i] == -1:  # True Negative
                tn += 1
            elif y_test[i] == 1 and y_pred[i] == 1:  # True Positive
                tp += 1
            elif y_test[i] == -1 and y_pred[i] == 1:  # False Positive
                fp += 1
            elif y_test[i] == 1 and y_pred[i] == -1:  # False Negative
                fn += 1


        # Menghitung metrik
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
        # ========================================== evaluasi model ================================================
        cm = confusion_matrix(y_test, y_pred, labels=model.classes_)

        cm_display = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=model.classes_)
        cm_display.plot(cmap='Blues', values_format='d')
        confusion_matrix_path = os.path.join("static", "images", "confusion_matrix.png")
        plt.savefig(confusion_matrix_path)
        plt.close()

        # ========================================== worldcloud ================================================
        # Mengambil teks untuk kelas 'positive', 'negative'
        positive_list = []
        negative_list = []

        # Iterasi data untuk memisahkan berdasarkan label
        for record in data_tfidf:
            if record.labels.lower() == 'positif':
                positive_list.append(record.preprocessing_text)
            elif record.labels.lower() == 'negatif':
                negative_list.append(record.preprocessing_text)

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

        return render_template(
        'klasifikasi.html',
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1=f1,
        wordcloud_images=wordcloud_images,
        report=report,
        klasifikasiTesting=klasifikasiTesting
        )


    except Exception as error:
        flash(f"Terjadi kesalahan saat pelatihan SVM: {str(error)}", "danger")
        return jsonify({"error": str(error)}), 500
        # return redirect(url_for('implementasiSvm.implementasiSvm'))
