import os

from flask import Flask,render_template,request, url_for, send_from_directory

from flask_restful import Resource, Api
from flask_restful import marshal_with,fields,reqparse

from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy

from models import comment, follow, like, blog, user
import datetime
from werkzeug.utils import secure_filename


engine = None
Base = declarative_base()
db = SQLAlchemy()



app= None
api= None

class config():
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class localconfig(config):
    SQLITE_DB_DIR = os.path.join(basedir, "../db_directory")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "myproject.sqlite3")
    DEBUG = True



imageupload = 'uploads\posts'



def create_app():  
    app = Flask(__name__, template_folder="templates")
    app.config['UPLOAD_FOLDER'] = imageupload
    if os.getenv('ENV', "development") == "production":
      raise Exception("Currently no production config is setup.")
    else:
      print("Staring Local Development")
    app.config.from_object(localconfig)
    db.init_app(app)
    api=Api(app)
    app.app_context().push()
    return app,api

app ,api= create_app()


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/', methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form("username")
        password = request.form("password")
        user = user.query.filter_by(username= username password = password).first()
    if user is not None:    
        msg= "Login successfully"
        return render_template('home.html',msg = msg)
    else:
        msg = 'Incorrect username / password !'
        return render_template('login.html', msg = msg)

@app.route('/home')
def home():
    followinguserdetails=[]
    likedetails=[]
    follows = Follow.query.filter_by(follower_username=current_user.username).all()
    for follow in follows:
        following_list.append(follow.followed_username)
    
    posts=Post.query.filter(Post.username.in_(following_list)).order_by(Post.timestamp.desc()).all()
    likes = Like.query.filter_by(username=current_user.username).all()
    for like in likes:
        liked_list.append(like.post_id)
    timestamp = datetime.datetime.now()

    return render_template('index.html', username=current_user.username, posts=posts , liked_list=liked_list , timestamp=timestamp)





@app.route('/Create New', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        yearofbirth=request.form.get("yearofbirth")
        
        user = user.query.filter_by(username=username)
        if user is None:
            user = User(username=username, password=password, yearofbirth=yearofbirth)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('home.html', username=username))
        else:
            return render_template("register.html", message="This username already exists!!!")
    return render_template("register.html")


@app.route('/Forgot Password?', methods=["GET", "POST"])
def forgotpw():
    if request.method == "POST":
        yearofbirth = request.form.get("yearofbirth")
        username= request.form.get("username")
        
        user = user.query.filter_by(username= username, yearofbirth= yearofbirth)
        if user is not None:
            user = User(username=username, password=password)
            return render_template("forgotpw.html", yearofbirth=yearofbirth)
            db.session.add(user)
            db.session.commit()


@app.route('/user/<username>')
def user(username):

    blog = blog.query.filter_by(username=username).fetchall()
    user = user.query.filter_by(username=username).first()
    already_follow=False
    follow = Follow.query.filter_by(
        follower_username=current_user.username, followed_username=username).first()
    if follow is not None:
        already_follow=True

    return render_template("user.html", posts=posts, username=username,already_follow=already_follow, current_user=current_user.username, user=user)



@app.route('/search', methods=["GET", "POST"])
def search():

    if request.method == "POST":
        search = request.form.get("search")
        users = user.query.filter(User.username.like('%'+search+'%')).all()
        return render_template("search.html", users=users, username=current_user.username)
    return render_template("search.html")


@app.route('/addnewBlog/<username>', methods=["GET", "POST"])
def addnewblog(username):
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        username = username
        timestamp = datetime.datetime.now()
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = url_for('uploaded_file', filename=filename)
        else:
            image_url = None
        user = User.query.filter_by(username=username).first()
        user.total_posts += 1
        post = Post(title=title, content=content, username=username,
                    timestamp=timestamp, image=image)
        db.session.add(post)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('home', username=username))
    return render_template("addnewblog.html", username=username)

@app.route('/like/<blog_id>/<username>')
def like(blog_id,username):
    like=like.query.filter_by(blog_id=blog_id,username=username).first()
    if like is None:
        post = blog.query.filter_by(blog_id=blog_id).first()
        blog.likes += 1
        timestamp=datetime.datetime.now()
        like=like(blog_id=blog_id,username=username,timestamp=timestamp)
        db.session.add(like)
        db.session.add(post)
        db.session.commit()
    return redirect(url_for('home', username=username))

@app.route('/unlike/<blog_id>/<username>')
def unlike(blog_id,username):
    like=like.query.filter_by(blog_id=blog_id,username=username).first()
    if like is not None:
        post = blog.query.filter_by(blog_id=blog_id).first()
        blog.likes -= 1
        db.session.add(post)
        db.session.delete(like)
        db.session.commit()
    return redirect(url_for('home', username=username))


@app.route('/comment/<blog_id>/<username>',methods=["GET","POST"])
def comment(blog_id,username):
    comments=comment.query.filter_by(blog_id=blog_id).all()
    if request.method == "POST":
        comment=request.form.get("comment")
        timestamp=datetime.datetime.now()
        comment=comment(blog_id=blog_id,username=username,comment=comment,timestamp=timestamp)
        post=post.query.filter_by(blog_id=blog_id).first()
        blog.comments+=1
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('home',username=username))
    
    return render_template('comment.html',username=username,comments=comments)

@app.route('/follow/<username>')
def follow(username):
    follow = Follow.query.filter_by(
        follower_username=current_user.username, followed_username=username).first()
    if follow is None:
        user = User.query.filter_by(username=username).first()

        current_user.number_of_following += 1
        user.number_of_followers += 1
        timestamp = datetime.datetime.now()
        follow = Follow(follower_username=current_user.username,
                        followed_username=username, timestamp=timestamp)
        db.session.add(user)
        db.session.add(current_user)
        db.session.add(follow)
        db.session.commit()
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
def unfollow(username):
    follow = follow.query.filter_by(
        follower_username=current_user.username, followed_username=username).first()
    if follow is not None:
        user = user.query.filter_by(username=username).first()
        current_user.no_followed -= 1
        user.no_followedby -= 1
        db.session.add(user)
        db.session.add(current_user)
        db.session.delete(follow)
        db.session.commit()
    return redirect(url_for('user', username=username))


@app.route('/<username>/followers')
def followers(username):
    follows = follow.query.filter_by(followed_username=username).all()
    return render_template('followers.html', follows=follows, username=username)


@app.route('/<username>/following')
def following(username):
    print(username)
    follows = follow.query.filter_by(follower_username=username).all()
    return render_template('following.html', follows=follows, username=username)


if __name__ == '__main__':
    app.run()

