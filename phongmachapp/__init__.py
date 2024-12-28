from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
from flask_login import LoginManager
import cloudinary
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/quanlyphongmachtudb?charset=utf8mb4" % quote('Admin@123')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SECRET_KEY"]="PhongDoLaNhatThoi_DangCapLaMaiMai"


cloudinary.config(
    cloud_name = "df5wj9kts",
    api_key = "749416224115579",
    api_secret = "4Kfje5f-cxS0KQfILzW1SwegeWE", # Click 'View API Keys' above to copy your API secret
)

app.config['NUM_PATIENT_PER_DAY']=40
app.config['MEDICAL_FEE']=100000
app.config['PAGE_SIZE'] = 7
medical_fee=app.config['MEDICAL_FEE']
num_patient_per_day=app.config['NUM_PATIENT_PER_DAY']

login=LoginManager(app)
db = SQLAlchemy(app)