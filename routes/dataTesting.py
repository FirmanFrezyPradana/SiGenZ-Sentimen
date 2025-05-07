from flask import Blueprint,render_template, flash
from db_config import db
from models import DataTesting
dataTesting_bp = Blueprint('dataTesting', __name__)

@dataTesting_bp.route('/hal_DataTesting',methods=['GET'])
def dataTesting():
    try:
        data = DataTesting.query.all()
        return render_template('data_testing.html', data=data)
    except Exception as e:
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
        return render_template('data_testing.html', data=[])