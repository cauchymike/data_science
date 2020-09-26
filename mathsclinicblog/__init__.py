#this is the __init__.py file under the mathsclinic blog folder
import os
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_mail import Message
from flask_sqlalchemy import SQLAlchemy
from flaskext.markdown import Markdown
from threading import Thread
import smtplib, ssl
from flask_pagedown import PageDown
from os import environ, path
import pymysql
from mathsclinicblog.filters import datetimeformat, file_type
from dotenv import load_dotenv




app = Flask(__name__)




############################
### DATABASE SETUP ##########
########################
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

app.config['SECRET_KEY'] = "jdhblfihriujromeyd8posi09547flujhcku53igkyudgsv423u76igsd7i6qwr72358ud90dxh8o387ds"
app.config['SQLALCHEMY_DATABASE_URI']= environ.get('CLEARDB_DATABASE_URL') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MATHSCLINIC_MAIL_SUBJECT_PREFIX'] = 'DSME blog'
app.config['MATHSCLINIC_MAIL_SENDER'] = 'michealakinkuotu6@gmail.com'
app.config['MATHSCLINIC_ADMIN'] = 'michealakinkuotu6@gmail.com'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'michealakinkuotu6@gmail.com'
app.config['MAIL_PASSWORD'] = 'seunmelody'
app.config["S3_BUCKET"] = "mathsclinic"
app.config["S3_KEY"] =  "AKIAJQB6S2LEVNKNBYNQ"
app.config["S3_SECRET"] = "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"
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MATHSCLINICCOMMENT_COMMENTS_PER_PAGE"] = 30
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['file_type'] = file_type
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_size":20,
    "pool_pre_ping":True,
    "pool_recycle": 3600,
}

S3_BUCKET = os.environ.get("S3_BUCKET")
S3_KEY = os.environ.get("S3_KEY")
S3_SECRET = os.environ.get("S3_SECRET_ACCESS_KEY")
#app.config['ADMINS'] = ['michealakinkuotu6@gmail.com']


mail = Mail(app)
db = SQLAlchemy(app)
Migrate(app,db)
pagedown = PageDown(app)
Markdown(app)


#########################
# LOGIN CONFIGS
login_manager = LoginManager()

login_manager.init_app(app)
login_manager.login_view = 'users.login'




from mathsclinicblog.core.views import core
from mathsclinicblog.users.views import users
from mathsclinicblog.blogpost.views import blog_posts
from mathsclinicblog.comments.views import comments_page
from mathsclinicblog.errorpages.handlers import error_pages

#we use blueprint to connect all our views together
app.register_blueprint(core)
app.register_blueprint(users)
app.register_blueprint(blog_posts)
app.register_blueprint(error_pages)
app.register_blueprint(comments_page)

