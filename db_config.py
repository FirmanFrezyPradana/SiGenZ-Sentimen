# import mysql.connector

# DB_CONFIG = {
#     "host": "localhost",
#     "user": "root",
#     "password": "",
#     "database": "Genz_sentimen"
# }


# def connect_db():
#     try:
#         connection = mysql.connector.connect(**DB_CONFIG)
#         if connection.is_connected():
#             print("✅ Berhasil terhubung ke database MySQL!")

#              # Set nilai max_allowed_packet jadi 64MB (67108864 byte)
#             cursor = connection.cursor()
#             cursor.execute("SET GLOBAL max_allowed_packet=67108864")
#             cursor.close()
#         return connection
#     except mysql.connector.Error as err:
#         print(f"❌ Error connecting to MySQL: {err}")
#         return None

from flask_sqlalchemy import SQLAlchemy
# Inisialisasi SQLAlchemy
db = SQLAlchemy()
