import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort,jsonify
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm_s,RegistrationForm_p, LoginForm, UpdateAccountForm, PostForm , CommentForm,DateForm
from flaskblog.models import User, Post ,Comment
from flask_login import login_user, current_user, logout_user, login_required
from dateutil import parser

@app.route("/",methods=['GET', 'POST'])
@app.route("/home_s",methods=['GET', 'POST'])
def home_s():
    form = DateForm()
    data = form.date.data
    if form.validate_on_submit():
        date = parser.parse(form.date.data)
        posts = Post.query.filter(Post.s_date <= date,Post.e_date >= date).all()
        posts1 =[] 
        for p in posts :
            if(p.author.a_type == "1"):
                posts1.append(p)
        return render_template('home.html', posts=posts1,formx=form)
    students = User.query.filter(User.a_type == 1)
    posts = [] 
    for s in students :
        for p in s.posts:
            posts.append(p)

    return render_template('home.html', posts=posts,formx=form)

@app.route("/home_p",methods=['GET', 'POST'])
def home_p():
    form = DateForm()
    data = form.date.data
    if form.validate_on_submit():
        date = parser.parse(form.date.data)
        posts = Post.query.filter(Post.s_date <= date,Post.e_date >= date).all()
        posts1 =[] 
        for p in posts :
            if(p.author.a_type == "2"):
                posts1.append(p)

        return render_template('home.html', posts=posts1,formx=form)
    providers = User.query.filter(User.a_type == 2)
    posts = [] 
    for s in providers :
        for p in s.posts:
            posts.append(p)

    return render_template('home.html', posts=posts,formx=form)

@app.route("/about")
def about():
    return render_template('about.html', title='About')




@app.route("/hall")
def hall():
    return render_template('hall.html', title='hallDetails')


@app.route("/register_s", methods=['GET', 'POST'])
def register_s():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm_s()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        _gender = request.form.get('gender')
        _group = request.form.get('group')
        user = User(username=form.username.data, email=form.email.data,
            password=hashed_password,s_gpa=form.s_gpa.data,h_gpa=form.h_gpa.data,a_type=1,address=form.address.data,group=_group,gender=_gender)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register_s.html', title='Register', form=form)


@app.route("/register_p", methods=['GET', 'POST'])
def register_p():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm_p()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        _gender = request.form.get('gender')
        user = User(username=form.username.data, email=form.email.data,
            password=hashed_password,dept=form.dept.data,a_type=2,hall=form.hall.data,gender=_gender)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register_p.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
           
            if(next_page):
                return redirect(next_page) 
            else:
                if(user.a_type == 1):
                    return redirect(url_for('home_s'))
                else:
                    return redirect(url_for('home_p'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home_s'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)



@app.route('/account/<int:user_id>')
@login_required
def show(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("show.html",user=user)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        s_date = parser.parse(form.s_date.data)
        e_date = parser.parse(form.e_date.data)
        post = Post(content=form.content.data,s_date=s_date,e_date=e_date, author=current_user)
        k = int(post.author.a_type)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        if(k == 1):
            return redirect(url_for('home_s'))
        else :
            return redirect(url_for('home_p'))
    return render_template('create_post.html', legend= "Your Question",title='New Post',
                           form=form)


@app.route("/post/<int:post_id>",methods=['GET', 'POST'])
@login_required
def post(post_id):
    form = CommentForm()
    post = Post.query.get_or_404(post_id)

    if form.validate_on_submit():
        comment = Comment(content=form.content.data,main_post=post,author=current_user)
        db.session.add(comment)
        db.session.commit()
        flash('You just commented on this post', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.content.data = ""
    return render_template('post.html', title=post.content, post=post,form=form,legend="Comment")


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    k = int(post.author.a_type)
    if post.author != current_user:
        abort(403)
    comments = post.comments
    for c in comments :
        db.session.delete(c)
    # db.session.commit()
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    if(k == 1):
        return redirect(url_for('home_s'))
    else :
        return redirect(url_for('home_p'))

@app.route("/comment/<int:comment_id>/update", methods=['GET', 'POST'])
@login_required
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.author != current_user:
        abort(403)
    form = CommentForm()
    if form.validate_on_submit():
        comment.content = form.content.data
        db.session.commit()
        flash('Your comment has been updated!', 'success')
        return redirect(url_for('post', post_id=comment.main_post.id))
    elif request.method == 'GET':
        form.content.data = comment.content
    return render_template('create_post.html', title='Update Comment',
                           form=form, legend='Update Comment')


@app.route("/comment/<int:comment_id>/delete", methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post = comment.main_post
    if comment.author != current_user:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('post',post_id=post.id))



@app.route("/livesearch",methods=['POST','GET'])
def livesearch():
    users = User.query.all()
    k = []
    for a in users :
        k.append(a.username)
    return jsonify(k)
