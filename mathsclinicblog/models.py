from mathsclinicblog import db,login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from datetime import datetime
from markdown import markdown
import bleach


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class Permission():
    COMMENT = 1

class User(db.Model,UserMixin):

    __tablename__ = 'users'

    id = db.Column(db.Integer,primary_key=True)
    profile_image = db.Column(db.String(64),nullable=False,default='default_profile.png')
    email = db.Column(db.String(64),unique=True,index=True)
    username = db.Column(db.String(64),unique=True,index=True)
    class_name = db.Column(db.String(20), unique = False, nullable = False)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.Text())
    age = db.Column(db.String(30), nullable = False )
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)
    

    posts = db.relationship('BlogPost',backref='author',lazy=True)#one to many relationship with blogposts
    comments = db.relationship('Comment', backref='user_comment', lazy='dynamic')#one to any relationship with comments
    #this backref is what we will call in the template and view functions
    def __init__(self,email,username,password,class_name, about_me, age):
        self.email = email
        self.username = username
        self.class_name = class_name
        self.age = age
        self.about_me = about_me
        self.password_hash = generate_password_hash(password)


    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    
    #web development with flask oreilly
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:#this helps us check that the id from the user matches the logged-in user
            return False
        self.confirmed = True#updating the confirmed column
        db.session.add(self)
        return True
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    
    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password_hash = generate_password_hash(new_password)
        db.session.add(user)
        return True
    
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def __repr__(self):
        return f"Username {self.username}"
    

class BlogPost(db.Model):

    __tablename__ = 'posts'

    users = db.relationship(User)

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)

    date = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    title = db.Column(db.String(140),nullable=False)
    text = db.Column(db.Text,nullable=False)
    comments = db.relationship('Comment', backref='comment_user', lazy = 'dynamic')

    def __init__(self,title,text,user_id):
        self.title = title
        self.text = text
        self.user_id = user_id

    def __repr__(self):
        return f"Post ID: {self.id} -- Date: {self.date} --- {self.title}"


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    #body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    #disabled = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __init__(self, body,user_id,post_id):
        self.body = body
        self.user_id = user_id
        self.post_id = post_id

    def __repr__(self):
        return f"Post ID: {self.id} -- Date: {self.date} --- {self.title}"


    