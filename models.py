import os
from flask import Flask, render_template,request
from flask_sqlalchemy import SQLAlchemy

current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "myproject.sqlite3") 
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable= False)
    total_posts = db.Column(db.Integer, default=0)
    no_followed = db.Column(db.Integer, default=0)
    no_followedby = db.Column(db.Integer, default=0)
    yearofbirth=db.Column(db.Integer,nullable=False)

class Blog(db.Model):
    __tablename__ = 'blog'
    blog_id = db.Column(db.Integer, primary_key = True)
    username= db.Column(db.String, db.ForeignKey("user.username"), nullable = False)
    title= db.Column(db.String, nullable = False)
    content= db.Column(db.String)
    image =  db.Column(db.String)
    timestamp = db.Column(db.DateTime,nullable= False)
    likes = db.Column(db.Integer)
    comments = db.Column(db.Integer)

class Comment(db.Model):
    __tablename__ = 'comment'
    comment_id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer, db.ForeignKey("blog.blog_id"), nullable=False)
    username= db.Column(db.String, db.ForeignKey("user.username"), nullable = False)
    timestamp = db.Column(db.DateTime, nullable= False)
    comment = db.Column(db.String, nullable = False)

class Likes(db.Model):
    __tablename__ = 'like'
    like_id = db.Column(db.Integer, primary_key= True)
    blog_id = db.Column(db.Integer, db.ForeignKey("blog.blog_id"), nullable=False)
    username= db.Column(db.String, db.ForeignKey("user.username"), nullable = False)
    timestamp = db.Column(db.DateTime, nullable= False)

class Follow(db.Model):
    __tablename__= 'follow'
    follow_id = db.Column(db.Integer, primary_key=True)
    followed = db.Column(db.String, db.ForeignKey("user.username"), nullable = False)
    followedby = db.Column(db.String, db.ForeignKey("user.username"), nullable = False)
    timestamp = db.Column(db.DateTime, nullable= False)



    


    

    
