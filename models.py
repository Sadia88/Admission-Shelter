from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    s_gpa = db.Column(db.Numeric(2,2),nullable=True)
    h_gpa = db.Column(db.Numeric(2,2),nullable=True)
    address = db.Column(db.String(20), unique=False, nullable=True)
    group = db.Column(db.String(10),nullable =True)
    gender = db.Column(db.String(10),nullable = False)
    password = db.Column(db.String(60), nullable=False)
    dept = db.Column(db.String(10),nullable = True)
    a_type = db.Column(db.String(20), nullable=False)
    hall = db.Column(db.String(10),nullable = True) 
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship("Comment",backref='author',lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    s_date = db.Column(db.DateTime, nullable=False)
    e_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment',backref='main_post',lazy=True)

    def __repr__(self):
        return f"Post('{self.content}', '{self.date_posted}')"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer,db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return "It is a comment for post {} , commented by user {}".format(self.post_id,self.user_id)
