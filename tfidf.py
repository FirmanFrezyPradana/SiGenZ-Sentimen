
# import math
# from collections import defaultdict
# from collections import defaultdict
# import pandas as pd

# # Menghitungg TF
# def compute_tf(documents):
#     ## sama seperti jurnal
#     tf_list = []
#     for doc in documents:
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
#     total_docs = len(documents)
#     word_set = set(word for doc in documents for word in doc.split())
#     for word in word_set:
#         doc_count = sum(1 for doc in documents if word in doc.split())
#         # Menghindari log(0) dengan pengecekan
#         # idf[word] = math.log10(total_docs / (doc_count + 1))  # Menambahkan 1 untuk menghindari pembagian dengan 0
#         ## menual
#         idf[word] = math.log10(total_docs / doc_count)
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


# # menggunakan library
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
