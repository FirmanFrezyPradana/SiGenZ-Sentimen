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
        stopword = factory.get_stop_words()
        more_stopword = [
            "ada", "adalah", "adanya", "adapun", "agak", "agaknya", "agar", "akan", "akankah",
            "akhir", "akhiri", "akhirnya", "aku", "akulah", "amat", "amatlah", "anda", "andalah",
            "antar", "antara", "antaranya", "apa", "apaan", "apabila", "apakah", "apalagi", "apatah",
            "artinya", "asal", "asalkan", "atas", "atau", "ataukah", "ataupun", "awal", "awalnya",
            "bagai", "bagaikan", "bagaimana", "bagaimanakah", "bagaimanapun", "bagi", "bagian", "bahkan",
            "bahwa", "bahwasanya", "baik", "bakal", "bakalan", "balik", "banyak", "bapak", "baru", "bawah",
            "beberapa", "begini", "beginian", "beginikah", "beginilah", "begitu", "begitukah", "begitulah",
            "begitupun", "bekerja", "belakang", "belakangan", "belum", "belumlah", "benar", "benarkah",
            "benarlah", "berada", "berakhir", "berakhirlah", "berakhirnya", "berapa", "berapakah", "berapalah",
            "berapapun", "berarti", "berawal", "berbagai", "berdatangan", "beri", "berikan", "berikut",
            "berikutnya", "berjumlah", "berkali-kali", "berkata", "berkehendak", "berkeinginan", "berkenaan",
            "berlainan", "berlalu", "berlangsung", "berlebihan", "bermacam", "bermacam-macam", "bermaksud",
            "bermula", "bersama", "bersama-sama", "bersiap", "bersiap-siap", "bertanya", "bertanya-tanya",
            "berturut", "berturut-turut", "bertutur", "berujar", "berupa", "besar", "betul", "betulkah",
            "biasa", "biasanya", "bila", "bilakah", "bisa", "bisakah", "boleh", "bolehkah", "bolehlah", "buat",
            "bukan", "bukankah", "bukanlah", "bukannya", "bulan", "bung", "cara", "caranya", "cukup", "cukupkah",
            "cukuplah", "cuma", "dahulu", "dalam", "dan", "dapat", "dari", "daripada", "datang", "dekat", "demi",
            "demikian", "demikianlah", "dengan", "depan", "di", "dia", "diakhiri", "diakhirinya", "dialah",
            "diantara", "diantaranya", "diberi", "diberikan", "diberikannya", "dibuat", "dibuatnya", "didapat",
            "didatangkan", "digunakan", "diibaratkan", "diibaratkannya", "diingat", "diingatkan", "diinginkan",
            "dijawab", "dijelaskan", "dijelaskannya", "dikarenakan", "dikatakan", "dikatakannya", "dikerjakan",
            "diketahui", "diketahuinya", "dikira", "dilakukan", "dilalui", "dilihat", "dimaksud", "dimaksudkan",
            "dimaksudkannya", "dimaksudnya", "diminta", "dimintai", "dimisalkan", "dimulai", "dimulailah",
            "dimulainya", "dimungkinkan", "dini", "dipastikan", "diperbuat", "diperbuatnya", "dipergunakan",
            "diperkirakan", "diperlihatkan", "diperlukan", "diperlukannya", "dipersoalkan", "dipertanyakan",
            "dipunyai", "diri", "dirinya", "disampaikan", "disebut", "disebutkan", "disebutkannya", "disini",
            "disinilah", "ditambahkan", "ditandaskan", "ditanya", "ditanyai", "ditanyakan", "ditegaskan",
            "ditujukan", "ditunjuk", "ditunjuki", "ditunjukkan", "ditunjukkannya", "ditunjuknya", "dituturkan",
            "dituturkannya", "diucapkan", "diucapkannya", "diungkapkan", "dong", "dua", "dulu", "empat", "enggak",
            "enggaknya", "entah", "entahlah", "guna", "gunakan", "hal", "hampir", "hanya", "hanyalah", "hari",
            "harus", "haruslah", "harusnya", "hendak", "hendaklah", "hendaknya", "hingga", "ia", "ialah", "ibarat",
            "ibaratkan", "ibaratnya", "ibu", "ikut", "ingat", "ingat-ingat", "ingin", "inginkah", "inginkan",
            "ini", "inikah", "inilah", "itu", "itukah", "itulah", "jadi", "jadilah", "jadinya", "jangan", "jangankan",
            "janganlah", "jauh", "jawab", "jawaban", "jawabnya", "jelas", "jelaskan", "jelaslah", "jelasnya", "jika",
            "jikalau", "juga", "jumlah", "jumlahnya", "justru", "kala", "kalau", "kalaulah", "kalaupun", "kalian",
            "kami", "kamilah", "kamu", "kamulah", "kan", "kapan", "kapankah", "kapanpun", "karena", "karenanya",
            "kasus", "kata", "katakan", "katakanlah", "katanya", "ke", "keadaan", "kebetulan", "kecil", "kedua",
            "keduanya", "keinginan", "kelamaan", "kelihatan", "kelihatannya", "kelima", "keluar", "kembali",
            "kemudian", "kemungkinan", "kemungkinannya", "kenapa", "kepada", "kepadanya", "kesampaian",
            "keseluruhan", "keseluruhannya", "keterlaluan", "ketika", "khususnya", "kini", "kinilah", "kira",
            "kira-kira", "kiranya", "kita", "kitalah", "kok", "kurang", "lagi", "lagian", "lah", "lain", "lainnya",
            "lalu", "lama", "lamanya", "lanjut", "lanjutnya", "lebih", "lewat", "lima", "luar", "macam", "maka",
            "makanya", "makin", "malah", "malahan", "mampu", "mampukah", "mana", "manakala", "manalagi", "masa",
            "masalah", "masalahnya", "masih", "masihkah", "masing", "masing-masing", "mau", "maupun", "melainkan",
            "melakukan", "melalui", "melihat", "melihatnya", "memang", "memastikan", "memberi", "memberikan",
            "membuat", "memerlukan", "memihak", "meminta", "memintakan", "memisalkan", "memperbuat", "mempergunakan",
            "memperkirakan", "memperlihatkan", "mempersiapkan", "mempersoalkan", "mempertanyakan", "mempunyai",
            "memulai", "memungkinkan", "menaiki", "menambahkan", "menandaskan", "menanti", "menanti-nanti",
            "menantikan", "menanya", "menanyai", "menanyakan", "mendapat", "mendapatkan", "mendatang", "mendatangi",
            "mendatangkan", "menegaskan", "mengakhiri", "mengapa", "mengatakan", "mengatakannya", "mengenai",
            "mengerjakan", "mengetahui", "menggunakan", "menghendaki", "mengibaratkan", "mengibaratkannya",
            "mengingat", "mengingatkan", "menginginkan", "mengira", "mengucapkan", "mengucapkannya", "mengungkapkan",
            "menjadi", "menjawab", "menjelaskan", "menuju", "menunjuk", "menunjuki", "menunjukkan", "menuturkan",
            "menyampaikan", "menyatakan", "menyebut", "menyebutkan", "menyebutkannya", "menyembunyikan",
            "menyertakan", "merasa", "merupakan", "meskipun", "mereka", "merekalah", "merupakan", "meskipun",
            "mesti", "mungkin", "mungkinkah", "mungkinlah", "nah", "nama", "nanti", "nanti-nanti", "nantinya",
            "negeri", "nggak", "nggaknya", "ni", "no", "oleh", "olehkarena", "olehkarenaitu", "olehsebabitu",
            "pada", "padahal", "pada", "paling", "paling-paling", "palingnya", "para", "penting", "per", "pergi",
            "pertama", "pertama-tama", "perusahaan", "pihak", "pihaknya", "proses", "rasa", "rasanya", "saat", "saatnya",
            "saja", "sajalah", "salam", "sama", "samalah", "sangat", "sangatlah", "sangatpun", "saya", "sayalah", "se",
            "seakan", "seakan-akan", "seandainya", "sebaliknya", "sebagaimana", "sebagaimanapun", "sebagian",
            "sebaliknya", "sebelum", "sebelumnya", "sebentar", "sebuah", "sebuahnya", "sehingga", "sekadar",
            "sekali", "sekalipun", "sekarang", "sekaranglah", "sekarangpun", "seperti", "sepertinya", "sepuluh",
            "sesama", "sesuatu", "sesuatunya", "seusia", "setelah", "setelahnya", "setiap", "setidaknya",
            "setuju", "setujuan", "siapa", "siapakah", "siapapun", "sini", "sinilah", "siswa", "sudah", "sudahlah",
            "sudahkan", "sudahkah", "sudahpun", "suka", "sukakah", "sukanya", "supaya", "tak", "tapi", "tahap", "tahapnya",
            "tanpa", "tanya", "tanyakan", "tanyanya", "tempat", "terakhir", "terakhirnya", "terdapat", "terdapatkan",
            "terhadap", "terhadapnya", "terjadi", "terjadilah", "terjadinya", "terlihat", "terlihatnya", "termasuk",
            "ternyata", "tersebut", "tersebutlah", "tersedia", "terserah", "terus", "teruslah", "terusnya",
            "tetap", "tetaplah", "tetapnya", "tidak", "tidakkah", "tidaklah", "tidaknya", "tinggal", "tinggalah",
            "tujuh", "tunggu", "tunggu-tunggu", "tungguin", "tungguinlah", "untuk", "untuknya", "usai", "usah", "yaitu",
            "yakin", "yakinkah", "yakinkan", "mu","nya","an","bang",
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
            cursor.execute("SELECT teks,labels FROM data_sentimen")
            data_sentimen = [{"teks": row[0], "labels": row[1]} for row in cursor.fetchall()]
        connection.close()

        # Cek apakah data kosong
        if not data_sentimen:
            flash("Tidak ada data yang tersedia untuk preprocessing.", "danger")
            return redirect(url_for('preprocessing.page_preprocessing'))

        # Ubah hasil query menjadi DataFrame
        df = pd.DataFrame(data_sentimen, columns=["teks","labels"])
        # df["teks"] = df["teks"].astype(str)  # Pastikan bertipe string
        # df = preprocess_texts(df["teks"].tolist())  # Preprocessing teks

        teks_list = [item['teks'] for item in data_sentimen]
        labels_list = [item['labels'] for item in data_sentimen]
        df = preprocess_texts(teks_list, labels_list)




        # Simpan hasil ke database, cek duplikasi terlebih dahulu
        connection = connect_db()
        with connection.cursor() as cursor:
            # Hapus teks yang sudah ada di preprocessing agar tidak duplikat
            cursor.execute("DELETE FROM preprocessing WHERE teks IN (SELECT teks FROM data_sentimen)")
            connection.commit()

            # Masukkan data yang belum ada
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
            connection.commit()

            # Hapus duplikat dalam tabel preprocessing, simpan satu saja
            cursor.execute("""
                DELETE FROM preprocessing
                WHERE id NOT IN (
                    SELECT MIN(id) FROM preprocessing GROUP BY teks
                )
            """)
            connection.commit()

        connection.close()
        flash("Preprocessing berhasil dilakukan!", "success")
        return redirect(url_for('preprocessing.page_preprocessing'))

    except Exception as error:
        flash(f"Terjadi kesalahan: {error}", "danger")
        return redirect(url_for('preprocessing.page_preprocessing'))
