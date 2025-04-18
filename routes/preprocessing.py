import pandas as pd
import re
import nltk
from nltk.tokenize import word_tokenize
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from flask import Blueprint, redirect, url_for, flash,render_template,request,jsonify
from db_config import connect_db

preprocessing_bp = Blueprint("preprocessing", __name__)

@preprocessing_bp.route('/page_preprocessing')
def page_preprocessing():
    connection = connect_db()
    if not connection:
        flash('Koneksi ke database gagal', 'error')
        return redirect(url_for('preprocessing.page_preprocessing'))
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT teks,labels, cleaned_text, lower_text,tokenized_text,normalized_text,stopword_text,preprocessing_text FROM preprocessing")
        data = cursor.fetchall()
        return render_template('pre_processing.html',data=data)
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
        return redirect(url_for('preprocessing.page_preprocessing'))

# Cleaning text
def cleaning_text(text):
    text = re.sub(r'http\S+|www\.\S+', '', text)
    text = re.sub(r'<br>', ' ', text)
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

# # Stopword
def stopword_removal(text):
    try:
        factory = StopWordRemoverFactory()
        stopword = factory.get_stop_words()
        more_stopword = [
            "a", "ak", "abc", "acc", "acoe", "ah", "bola", "bla", "uec", "beuh", "ayo", "bu", "b", "acom", "hahahahha","dekkkk","pol","gemezzz",
            "ada", "adu", "oe", "aldo", "akh", "aka", "aki", "all", "dmi", "enji", "khao", "urgh", "haha", "wkwkwkwkwkwk", "hhhhhhhhh","dekkkkkkkk",
            "cam", "ae", "alert", "afer", "agreed", "aides", "akn", "alur", "do", "eq", "fittest", "ishhh", "eh", "het", "wah","x","kan","ku","nih",
            "cahol", "aegyo", "aer", "ajer", "ai", "aids", "ala", "am", "dok", "etc", "anaoisanya", "wkwk", "aowkaowk", "uh", "ai","main fan fiction",
            "c", "camp", "can", "carats", "cc", "cek", "cekadak", "dik", "dong", "hoho", "euy", "ohhh", "amp", "ohhhhh", "amp","an","aaja","brooooo gas oke gas in",
            "centris", "centu", "ceo", "ckckck", "cot", "core", "deri", "dl", "duh", "belva", "wooooww", "ozaaaa", "wah", "isee",
            "cuba", "cuihh", "da", "dah", "bim", "deh", "diding", "dlk", "e", "quot", "ber", "uuhhh", "laaaaaaaaaaaaaaaaaaah",
            "cucuk", "cuy", "daei", "dahh", "dangg", "dek", "dih", "dm", "eh", "beibeh", "huuaaaaa", "hmmm", "wkwkwkwkwkwkw","amp","sih","nya","aku", "tahun","jam","pagi","coba","waktu","namanya","mulai","sore","anak","orang","kayak","intinya","semua"
        ]
        stop_words = factory.get_stop_words() + more_stopword
        return [word for word in text if word not in stop_words]

    except Exception as e:
        print(f"Error saat stopword removal: {e}")
        return text

# stemmed
def stemmed(text):
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    return [stemmer.stem(word) for word in text]

# Preprocessing function
def preprocess_texts(teks, labels):
    try:
        df = pd.DataFrame({'teks': teks, 'labels': labels})
        df['teks'] = df['teks'].astype(str)
        df['labels'] = df['labels'].astype(str)
        df['cleaning_text'] = df['teks'].apply(cleaning_text)
        df['lower_text'] = df['cleaning_text'].apply(case_folding)
        df['tokenized_text'] = df['lower_text'].apply(tokenizing)
        df['normalized_text'] = df['tokenized_text'].apply(normalisasi)
        df['stopword_text'] = df['normalized_text'].apply(stopword_removal)
        df['lemmatized_text'] = df['stopword_text'].apply(stemmed)
        return df
    except Exception as e:
        flash(f"terjadi kesalahan saat preprocessing data: {e}", "danger")
        return None

@preprocessing_bp.route('/preprocessing/proses', methods=['GET', 'POST'])
def preprocessing_data():
    if request.method == 'GET':
        return render_template("pre-processing.html")
    try:
        # Ambil data dari database
        connection = connect_db()
        with connection.cursor() as cursor:
            cursor.execute("SELECT teks,labels FROM data_sentimen")
            data_sentimen = [{"teks": row[0], "labels": row[1]} for row in cursor.fetchall()]

        # Cek apakah data kosong
        if not data_sentimen:
            flash("Tidak ada data yang tersedia untuk preprocessing.", "danger")
            return redirect(url_for('preprocessing.page_preprocessing'))

        # Ubah hasil query menjadi DataFrame
        df = pd.DataFrame(data_sentimen, columns=["teks","labels"])
        teks_list = [item['teks'] for item in data_sentimen]
        labels_list = [item['labels'] for item in data_sentimen]
        df = preprocess_texts(teks_list, labels_list)

        # Simpan hasil ke database
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE preprocessing")
            cursor.executemany(
                """
                INSERT INTO preprocessing (teks,labels, cleaned_text, lower_text, tokenized_text, normalized_text, stopword_text, preprocessing_text)
                VALUES (%s,%s, %s, %s, %s, %s, %s, %s)
                """,
                [(row["teks"],row["labels"], row["cleaning_text"], row["lower_text"],
                  ' '.join(row["tokenized_text"]), ' '.join(row["normalized_text"]),
                  ' '.join(row["stopword_text"]), ' '.join(row["lemmatized_text"]))
                 for _, row in df.iterrows()]
            )

            # Hapus duplikat dalam tabel preprocessing
            cursor.execute("""
                DELETE FROM preprocessing
                WHERE id NOT IN (
                    SELECT MIN(id) FROM preprocessing GROUP BY teks
                )
            """)
            # hapus data yang ada pada tabel
            cursor.execute("TRUNCATE TABLE data_tfidf")
            connection.commit()

        connection.close()
        flash("Preprocessing berhasil dilakukan!", "success")
        return redirect(url_for('preprocessing.page_preprocessing', status='preprocess_success'))

    except Exception as error:
        flash(f"Terjadi kesalahan: {error}", "danger")
        return redirect(url_for('preprocessing.page_preprocessing'))
