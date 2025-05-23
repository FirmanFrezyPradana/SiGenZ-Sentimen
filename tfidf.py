from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
def compute_tfidf(documents):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Konversi hasilnya ke DataFrame
    df_tfidf = pd.DataFrame(
        tfidf_matrix.toarray(),
        columns=vectorizer.get_feature_names_out()
    )

    return df_tfidf


# import math
# from collections import defaultdict
# import pandas as pd
# import pickle

# # Menghitungg TF
# def compute_tf(documents):
#     ## sama seperti jurnal
#     tf_list = []

#     # for doc in documents:
#     for doc in enumerate(documents):
#         # hitung kemunculan kata
#         tf_counts = defaultdict(int)
#         words = doc.split()
#         # Hitung frekuensi setiap kata dalam dokumen
#         for word in words:
#             tf_counts[word] += 1

#         # Hitung TF dengan skala logaritmik: TF = 1 + log10(frek)
#         tf_log_scaled = {
#             word: round(1 + math.log10(count), 4)
#             for word, count in tf_counts.items()
#         }
#         tf_list.append(tf_log_scaled)
#     return tf_list

# # Menghitung IDF
# def compute_idf(documents):
#     idf = {}
#     # simpan hasil doc_count
#     total_docs = len(documents)
#     word_set = set(word for doc in documents for word in doc.split())
#     for word in word_set:
#         doc_count = sum(1 for doc in documents if word in doc.split())
#         ## menual
#         idf[word] = math.log10(total_docs / doc_count) if doc_count > 0 else 0
#     return idf


# # Menghitung tf-idf
# def compute_tfidf(documents):
#     tf = compute_tf(documents)
#     idf = compute_idf(documents)
#     tfidf_list = []
#     for doc_tf in tf:
#         tfidf_doc = {word: tf_value * idf.get(word, 0) for word, tf_value in doc_tf.items()}
#         tfidf_list.append(tfidf_doc)
#     # Konversi ke DataFrame dan isi nilai NaN dengan 0
#     tfidf_df = pd.DataFrame(tfidf_list).fillna(0)
#     return tfidf_df


# def saveTFIDF(tfidf_df, idf):
#     # Ambil urutan vocab dari kolom tfidf_df dan urutkan sesuai vocal
#     vocab = list(tfidf_df.columns)
#     sorted_idf = {word: idf[word] for word in vocab}

#     # Simpan ke file pkl
#     with open('static/model/tfidf_vocab.pkl', 'wb') as f:
#         pickle.dump(vocab, f)
#     with open('static/model/tfidf_idf.pkl', 'wb') as f:
#         pickle.dump(sorted_idf, f)


# ##Fungsi untuk memproses kalimat baru menjadi vektor TF-IDF
# def transform(teks_baru):
#     # Load vocab dan IDF
#     with open('static/model/tfidf_vocab.pkl', 'rb') as f:
#         vocab = pickle.load(f)
#     with open('static/model/tfidf_idf.pkl', 'rb') as f:
#         idf = pickle.load(f)

#     # Hitung TF untuk kalimat baru
#     tf_counts = {}
#     words = teks_baru.split()
#     for word in words:
#         tf_counts[word] = tf_counts.get(word, 0) + 1
#     tf_log_scaled = {
#         word: 1 + math.log10(count) for word, count in tf_counts.items()
#     }

#     # Buat vektor TF-IDF sesuai urutan vocab
#     tfidf_vector = []
#     for word in vocab:
#         tf = tf_log_scaled.get(word, 0)
#         idf_val = idf.get(word, 0)
#         tfidf_vector.append(round(tf * idf_val, 6))
#     return tfidf_vector






