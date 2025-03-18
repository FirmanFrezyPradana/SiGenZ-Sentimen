import pandas as pd
import re
import nltk
from nltk.tokenize import word_tokenize
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from flask import Blueprint, redirect, url_for, flash,render_template,request,jsonify
from db_config import connect_db

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')

preprocessing_bp = Blueprint("preprocessing", __name__)

@preprocessing_bp.route('/page_preprocessing')
def page_preprocessing():
    connection = connect_db()
    if not connection:
        flash('Koneksi ke database gagal', 'error')
        return redirect(url_for('preprocessing.page_preprocessing'))
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT teks, cleaned_text, lower_text,tokenized_text,normalized_text,stopword_text,preprocessing_text FROM preprocessing")
        data = cursor.fetchall()
        return render_template('pre_processing.html',data=data)
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
        return redirect(url_for('preprocessing.page_preprocessing'))

# Cleaning text
def cleaning_text(text):
    text = re.sub(r'http\S+|www\.\S+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'@\S+', '', text)
    text = re.sub(r'['
                   u'\U0001F600-\U0001F64F'
                   u'\U0001F300-\U0001F5FF'
                   u'\U0001F680-\U0001F6FF'
                   u'\U0001F1E0-\U0001F1FF'
                    ']+', '', text)

    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\b(\w+)-\1\b', r'\1', text)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def case_folding(text):
    return text.lower()

def tokenizing(text):
    return word_tokenize(text)

normalisasi_kata_df = pd.read_csv('static/kamus/normalisasi-new.csv')
normalisasi_kata_dict = dict(zip(normalisasi_kata_df['before'], normalisasi_kata_df['after']))
def normalisasi(text):
    if isinstance(text, list):
        return [normalisasi_kata_dict.get(word, word) for word in text]
    return text

# # Stopword removal library
def stopword_removal(text):
    try:
        factory = StopWordRemoverFactory()
        stopword = factory.create_stop_word_remover()
        more_stopword = [
            "mu","nya","an","bang"
        ]
        stop_words = factory.get_stop_words() + more_stopword
        return [word for word in text if word not in stop_words]
    except Exception as e:
        print(f"Error saat stopword removal: {e}")
        return text

# stemmed
def lemmatization(text):
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    return [stemmer.stem(word) for word in text]

# Preprocessing function
def preprocess_texts(texts):
    try:
        df = pd.DataFrame(texts, columns=["teks"])
        df['teks'] = df['teks'].astype(str)
        df['cleaning_text'] = df['teks'].apply(cleaning_text)
        df['lower_text'] = df['cleaning_text'].apply(case_folding)
        df['tokenized_text'] = df['lower_text'].apply(tokenizing)
        df['normalized_text'] = df['tokenized_text'].apply(normalisasi)
        df['stopword_text'] = df['normalized_text'].apply(stopword_removal)
        df['lemmatized_text'] = df['stopword_text'].apply(lemmatization)

        return df
    except Exception as e:
        flash(f"Error in preprocessing: {e}", "danger")
        return None


@preprocessing_bp.route('/preprocessing/proses', methods=['GET', 'POST'])
def preprocessing_data():
    if request.method == 'GET':
        return render_template("pre-processing.html")

    try:
       # Ambil data dari database
        connection = connect_db()
        with connection.cursor() as cursor:
            cursor.execute("SELECT teks FROM data_sentimen")
            data_sentimen = [row[0] for row in cursor.fetchall()]
        connection.close()

        # Cek apakah data kosong
        if not data_sentimen:
            flash("Tidak ada data yang tersedia untuk preprocessing.", "danger")
            return redirect(url_for('preprocessing.page_preprocessing'))

        # Ubah hasil query menjadi DataFrame
        df = pd.DataFrame(data_sentimen, columns=["teks"])
        df["teks"] = df["teks"].astype(str)  # Pastikan bertipe string
        # Preprocessing data
        df = preprocess_texts(df["teks"].tolist())

        # Simpan hasil ke database
        connection = connect_db()
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE preprocessing")
            cursor.executemany(
                "INSERT INTO preprocessing (teks, cleaned_text, lower_text, tokenized_text, normalized_text, stopword_text, preprocessing_text) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                [(row["teks"], row["cleaning_text"], row["lower_text"], ' '.join(row["tokenized_text"]), ' '.join(row["normalized_text"]), ' '.join(row["stopword_text"]), ' '.join(row["lemmatized_text"])) for _, row in df.iterrows()]
            )

        connection.commit()
        connection.close()
        flash("Preprocessing berhasil dilakukan!", "success")
        return redirect(url_for('preprocessing.page_preprocessing'))

    except Exception as error:
        flash(f"Terjadi kesalahan: {error}", "danger")
        return redirect(url_for('preprocessing.page_preprocessing'))