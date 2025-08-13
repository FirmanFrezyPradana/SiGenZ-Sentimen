from .dashboard import dashboard_bp
from .dataSentimen import dataSentimen_bp
from .preprocessing import preprocessing_bp
from .pembobotan import pembobotan_bp
from .dataTraining import dataTraining_bp
from .dataTesting import dataTesting_bp
from .implementasi import implementasiSvm_bp
from .testing import testing_bp
from .cek import cek_bp

def register_blueprints(app):
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(dataSentimen_bp)
    app.register_blueprint(preprocessing_bp)
    app.register_blueprint(pembobotan_bp)
    app.register_blueprint(dataTraining_bp)
    app.register_blueprint(dataTesting_bp)
    app.register_blueprint(implementasiSvm_bp)
    app.register_blueprint(cek_bp)
    app.register_blueprint(testing_bp)
