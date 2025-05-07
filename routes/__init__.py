from .dashboard import dashboard_bp
from .dataSentimen import dataSentimen_bp
from .importData import import_bp
from .preprocessing import preprocessing_bp
from .pembobotan import pembobotan_bp
from .dataTraining import dataTraining_bp
from .dataTesting import dataTesting_bp
from .implementasi import implementasiSvm_bp

# from .traintest import traintest_bp
# from .testresult import testresult_bp
# from .register import register_bp
# from .login import login_bp
# from .admin_routes import admin_bp

def register_blueprints(app):
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(dataSentimen_bp)
    app.register_blueprint(import_bp)
    app.register_blueprint(preprocessing_bp)
    app.register_blueprint(pembobotan_bp)
    app.register_blueprint(dataTraining_bp)
    app.register_blueprint(dataTesting_bp)
    app.register_blueprint(implementasiSvm_bp)

    # app.register_blueprint(testresult_bp)
    # app.register_blueprint(register_bp)
    # app.register_blueprint(login_bp)
    # app.register_blueprint(admin_bp)
