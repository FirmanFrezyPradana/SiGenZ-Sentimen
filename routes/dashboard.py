
from flask import Blueprint, render_template
from models import DataSentimen, DataTraining, DataTesting,klasifikasiTestingModel
from sqlalchemy import func
dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')


@dashboard_bp.route('/')
def dashboard():
    jumlah_total = DataSentimen.query.count()
    jumlah_latih = DataTraining.query.count()
    jumlah_uji = DataTesting.query.count()
    jumlah_positif = DataSentimen.query.filter(DataSentimen.labels == 'positif').count()
    jumlah_negatif = DataSentimen.query.filter(DataSentimen.labels == 'negatif').count()

    dominan = (
        klasifikasiTestingModel.query
        .with_entities(klasifikasiTestingModel.label_prediksi)
        .group_by(klasifikasiTestingModel.label_prediksi)
        .order_by(func.count().desc())
        .first()
    )[0]


    return render_template("dashboard.html",
                           jumlah_latih=jumlah_latih,
                           jumlah_uji=jumlah_uji,
                           jumlah_total=jumlah_total,
                           jumlah_positif=jumlah_positif,
                           jumlah_negatif=jumlah_negatif,
                           dominan = dominan
                           )
