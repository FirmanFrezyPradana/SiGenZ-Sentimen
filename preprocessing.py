import re
import pandas as pd
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from nltk.tokenize import word_tokenize
from flask import flash

import nltk
nltk.download('punkt')
# mengambil file normalisasi.csv
normalisasi_kata_df = pd.read_csv('static/kamus/normalisasi-new.csv')
normalisasi_kata_dict = dict(zip(normalisasi_kata_df['before'], normalisasi_kata_df['after']))

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
    tokens = word_tokenize(text)
    # Gabungkan 'gen' + 'z' menjadi 'genz'= karena kata tersebut sering muncul
    i = 0
    while i < len(tokens) - 1:
        if tokens[i] == 'gen' and tokens[i + 1] == 'z':
            tokens[i] = 'genz'         # Gabungkan menjadi 'genz'
            del tokens[i + 1]          # Hapus 'z'
        else:
            i += 1
    return tokens

def normalisasi(text):
    if isinstance(text, list):
        return [normalisasi_kata_dict.get(word, word) for word in text]
    return text

# # Stopword
def stopword_removal(text):
    try:
        factory = StopWordRemoverFactory()
        stopword = factory.get_stop_words()
        # kecualikan karena kata tidak ambigu dalam hal penilaian
        custom_stopwords = list(filter(lambda x: x != 'tidak', stopword))
        more_stopword = [
            "a", "ak", "abc", "acc", "acoe", "ah", "bola", "bla", "uec", "beuh", "ayo", "bu", "b", "acom", "hahahahha","dekkkk","pol","gemezzz","bang",
            "ada", "adu", "oe", "aldo", "akh", "aka", "aki", "all", "dmi", "enji", "khao", "urgh", "haha", "wkwkwkwkwkwk", "hhhhhhhhh","dekkkkkkkk",
            "cam", "ae", "alert", "afer", "agreed", "aides", "akn", "alur", "do", "eq", "fittest", "ishhh", "eh", "het", "wah","x","kan","ku","nih",
            "cahol", "aegyo", "aer", "ajer", "ai", "aids", "ala", "am", "dok", "etc", "anaoisanya", "wkwk", "aowkaowk", "uh", "ai","main fan fiction",
            "c", "camp", "can", "carats", "cc", "cek", "cekadak", "dik", "dong", "hoho", "euy", "ohhh", "amp", "ohhhhh", "amp","an","aaja","brooooo gas oke gas in",
            "centris", "centu", "ceo", "ckckck", "cot", "core", "deri", "dl", "duh", "belva", "wooooww", "ozaaaa", "wah", "isee","lurr","lah","sana","sini",
            "cuba", "cuihh", "da", "dah", "bim", "deh", "diding", "dlk", "e", "quot", "ber", "uuhhh", "laaaaaaaaaaaaaaaaaaah","bro","nak","ya","for","your","guys",
            "cucuk", "cuy", "daei", "dahh", "dangg", "dek", "dih", "dm", "eh", "beibeh", "huuaaaaa", "hmmm", "wkwkwkwkwkwkw","amp","sih","nya","aku",
            "tahun","jam","pagi","coba","waktu","namanya","mulai","sore","anak","orang","kayak","intinya","semua","xixi","pov","iya","to","olga","paling"
            "ada", "adalah", "adanya", "adapun", "agak", "agaknya", "agar", "akan", "akankah", "akhir",
            "akhiri", "akhirnya", "aku", "akulah", "amat", "amatlah", "anda", "andalah", "antar", "antara",
            "antaranya", "apa", "apaan", "apabila", "apakah", "apalagi", "apatah", "artinya", "asal",
            "asalkan", "atas", "atau", "ataukah", "ataupun", "awal", "awalnya", "bagai", "bagaikan",
            "bagaimana", "bagaimanakah", "bagaimanapun", "bagi", "bagian", "bahkan", "bahwa", "bahwasanya",
            "baik", "bakal", "bakalan", "balik", "banyak", "bapak", "baru", "bawah", "beberapa", "begini",
            "beginian", "beginikah", "beginilah", "begitu", "begitukah", "begitulah", "begitupun", "bekerja",
            "belakang", "belakangan", "belum", "belumlah", "benar", "benarkah", "benarlah", "berada",
            "berakhir", "berakhirlah", "berakhirnya", "berapa", "berapakah", "berapalah", "berapapun",
            "berarti", "berawal", "berbagai", "berdatangan", "beri", "berikan", "berikut", "berikutnya",
            "berjumlah", "berkali-kali", "berkata", "berkehendak", "berkeinginan", "berkenaan", "berlainan",
            "berlalu", "berlangsung", "berlebihan", "bermacam", "bermacam-macam", "bermaksud", "bermula",
            "bersama", "bersama-sama", "bersiap", "bersiap-siap", "bertanya", "bertanya-tanya", "berturut",
            "berturut-turut", "bertutur", "berujar", "berupa", "besar", "betul", "betulkah", "biasa",
            "biasanya", "bila", "bilakah", "bisa", "bisakah", "boleh", "bolehkah", "bolehlah", "buat",
            "bukan", "bukankah", "bukanlah", "bukannya", "bulan", "bung", "cara", "caranya", "cukup",
            "cukupkah", "cukuplah", "cuma", "dahulu", "dalam", "dan", "dapat", "dari", "daripada",
            "datang", "dekat", "demi", "demikian", "demikianlah", "dengan", "depan", "di", "dia",
            "diakhiri", "diakhirinya", "dialah", "diantara", "diantaranya", "diberi", "diberikan",
            "diberikannya", "dibuat", "dibuatnya", "didapat", "didatangkan", "digunakan", "diibaratkan",
            "diibaratkannya", "diingat", "diingatkan", "diinginkan", "dijawab", "dijelaskan", "dijelaskannya",
            "dikarenakan", "dikatakan", "dikatakannya", "dikerjakan", "diketahui", "diketahuinya", "dikira",
            "dilakukan", "dilalui", "dilihat", "dimaksud", "dimaksudkan", "dimaksudkannya", "dimaksudnya",
            "diminta", "dimintai", "dimisalkan", "dimulai", "dimulailah", "dimulainya", "dimungkinkan",
            "dini", "dipastikan", "diperbuat", "diperbuatnya", "dipergunakan", "diperkirakan", "diperlihatkan",
            "diperlukan", "diperlukannya", "dipersoalkan", "dipertanyakan", "dipunyai", "diri", "dirinya",
            "disampaikan", "disebut", "disebutkan", "disebutkannya", "disini", "disinilah", "ditambahkan",
            "ditandaskan", "ditanya", "ditanyai", "ditanyakan", "ditegaskan", "ditujukan", "ditunjuk",
            "ditunjuki", "ditunjukkan", "ditunjukkannya", "ditunjuknya", "dituturkan", "dituturkannya",
            "diucapkan", "diucapkannya", "diungkapkan", "dong", "dua", "dulu", "empat", "enggak", "enggaknya",
            "entah", "entahlah", "guna", "gunakan", "hal", "hampir", "hanya", "hanyalah", "hari", "harus",
            "haruslah", "harusnya", "hendak", "hendaklah", "hendaknya", "hingga", "ia", "ialah", "ibarat",
            "ibaratkan", "ibaratnya", "ibu", "ikut", "ingat", "ingat-ingat", "ingin", "inginkah", "inginkan",
            "ini", "inikah", "inilah", "itu", "itukah", "itulah", "jadi", "jadilah", "jadinya", "jangan",
            "jangankan", "janganlah", "jauh", "jawab", "jawaban", "jawabnya", "jelas", "jelaskan", "jelaslah",
            "jelasnya", "jika", "jikalau", "juga", "jumlah", "jumlahnya", "justru", "kala", "kalau", "kalaulah",
            "kalaupun", "kalian", "kami", "kamilah", "kamu", "kamulah", "kan", "kapan", "kapankah", "kapanpun"
            "meminta", "memintakan", "memisalkan", "memperbuat","tahun","kok","mau","koh","okey"
        ]

        stop_words = custom_stopwords + more_stopword
        # stop_words = more_stopword
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
def preprocess_texts(teks, labels=None):
    try:
        df = pd.DataFrame({'teks': teks, 'labels': labels})
        df['teks'] = df['teks'].astype(str)
        df['labels'] = df['labels'].astype(str)
        df['cleaning_text'] = df['teks'].apply(cleaning_text)
        df['lower_text'] = df['cleaning_text'].apply(case_folding)
        df['tokenized_text'] = df['lower_text'].apply(tokenizing)
        df['normalized_text'] = df['tokenized_text'].apply(normalisasi)
        df['stopword_text'] = df['normalized_text'].apply(stopword_removal)
        df['hasil_text'] = df['stopword_text'].apply(stemmed)
        df['preprocessing_text'] = df['hasil_text'].apply(lambda x: ' '.join(x) if isinstance(x, list) else x)
        return df
    except Exception as e:
        flash(f"terjadi kesalahan saat preprocessing data: {e}", "danger")
        return None