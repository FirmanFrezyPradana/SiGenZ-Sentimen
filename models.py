from sqlalchemy import Column, Integer, String, Float
from db_config import db

class DataSentimen(db.Model):
    __tablename__ = 'data_sentimen'
    id = db.Column(db.Integer, primary_key=True)
    labels = db.Column(db.String(50))
    teks = db.Column(db.Text)
    sosmed = db.Column(db.String(50))

class DataTraining(db.Model):
    __tablename__ = 'data_training'
    id = db.Column(db.Integer, primary_key=True)
    teks = db.Column(db.Text)
    labels = db.Column(db.String(50))
    preprocessing_text = db.Column(db.Text)
    tfidf = db.Column(db.Text)

class DataTesting(db.Model):
    __tablename__ = 'data_testing'
    id = db.Column(db.Integer, primary_key=True)
    teks = db.Column(db.Text)
    labels = db.Column(db.String(50))
    preprocessing_text = db.Column(db.Text)
    tfidf = db.Column(db.Text)

class Preprocessing(db.Model):
    __tablename__ = 'preprocessing'
    id = db.Column(db.Integer, primary_key=True)
    teks = db.Column(db.Text)
    labels = db.Column(db.String(50))
    preprocessing_text = db.Column(db.Text)
class DataTFIDF(db.Model):
    __tablename__ = 'data_tfidf'
    id = db.Column(db.Integer, primary_key=True)
    teks = db.Column(db.Text)
    preprocessing_text = db.Column(db.Text)
    labels = db.Column(db.String(50))
    tfidf = db.Column(db.Text)
class klasifikasiTestingModel(db.Model):
    __tablename__ = 'klasifikasiTestingModel'
    id = db.Column(db.Integer, primary_key=True)
    teks = db.Column(db.Text, nullable=False)
    preprocessing = db.Column(db.Text, nullable=False)
    label_aktual = db.Column(db.String(10), nullable=False)
    label_prediksi = db.Column(db.String(10), nullable=False)

class testingModel(db.Model):
    __tablename__ = 'testing'
    id = db.Column(db.Integer, primary_key=True)
    teks = db.Column(db.Text, nullable=False)
    preprocessing = db.Column(db.Text, nullable=False)
    label_prediksi = db.Column(db.String(10), nullable=False)