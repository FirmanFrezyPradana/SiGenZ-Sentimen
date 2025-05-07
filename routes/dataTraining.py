from flask import Blueprint,redirect, url_for,render_template, flash
from db_config import db
from models import DataTraining

dataTraining_bp = Blueprint('dataTraining', __name__)

@dataTraining_bp.route('/hal_DataTraining',methods=['GET'])
def dataTraining():
    try:
        data = DataTraining.query.all()
        return render_template('data_training.html', data=data)
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
        return redirect(url_for('dataTraining.dataTraining',data=[]))