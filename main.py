from datetime import date
from flask import abort, Flask, flash, redirect, render_template, request, url_for
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from forms import CommentForm, CreatePostForm, RegisterForm, LoginForm
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import os
import smtplib

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
ckeditor = CKEditor(app)
Bootstrap(app)
app.app_context().push()


MY_EMAIL = os.environ['MY_EMAIL']
PASSWORD = os.environ['PASSWORD']

login_manager = LoginManager()
login_manager.init_app(app)

# Connect to DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


# Configure tables
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)

    post = relationship("BlogPost", back_populates="author")
    comment = relationship("Comment", back_populates="comment_author")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    author_id = db.Column(db.Integer, ForeignKey('users.id'))
    author = relationship("User", back_populates="post")

    parent_post = relationship("Comment", back_populates="blog_post")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)

    author_id = db.Column(db.Integer, ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comment")

    blog_post_id = db.Column(db.Integer, ForeignKey("blog_posts.id"))
    blog_post = relationship("BlogPost", back_populates="parent_post")


# db.create_all()


def is_admin():
    user = db.session.get(User, 1)
    if user == current_user:
        return True
    return False


# Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        user = db.session.get(User, 1)
        if user == current_user:
            return f(*args, **kwargs)
        # Otherwise continue with the route function
        return abort(403)

    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Routes
@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template('index.html', all_posts=posts, current_user=current_user, admin=is_admin())


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash_and_salted_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with this email, log in instead!")
            return redirect(url_for('login'))
        new_user = User(
            email=form.email.data,
            password=hash_and_salted_password,
            name=form.name.data
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('get_all_posts'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash("The email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, form.password.data):
            flash("Password incorrect, please try again.")
            return redirect(url_for("login"))
        elif user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('get_all_posts'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/post/<int:post_id>', methods=['POST', 'GET'])
def show_post(post_id):
    comment_form = CommentForm()
    requested_post = db.session.get(BlogPost, post_id)
    print('gravatar', gravatar)
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment")
            return redirect(url_for('login'))
        new_comment = Comment(
            text=comment_form.comment.data,
            comment_author=current_user,
            blog_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
    all_comments = db.session.query(Comment).all()
    comment_date = date.today().strftime("%B %d, %Y")
    return render_template('post.html', post=requested_post, form=comment_form, admin=is_admin(),
                           all_comments=all_comments, comment_date=comment_date)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        print(f"Name: {request.form['name']}\n"
              f"Email {request.form['email']}\n"
              f"Phone: {request.form['phone']}\n"
              f"Message: {request.form['message']}")

        with smtplib.SMTP('smtp.gmail.com', 587) as connection:
            connection.starttls()
            connection.login(user=request.form['email'], password=PASSWORD)
            connection.sendmail(
                from_addr=request.form['email'],
                to_addrs=MY_EMAIL,
                msg=f"Name: {request.form['name']}\n"
                    f"Email {request.form['email']}\n"
                    f"Phone: {request.form['phone']}\n"
                    f"Message: {request.form['message']}"

            )
        return render_template('contact.html', message_sent=True)
    elif request.method == "GET":
        return render_template('contact.html', message_sent=False)


@app.route('/new_post', methods=['GET', 'POST'])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y"),
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form=form, admin=is_admin())


@app.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
@admin_only
def edit_post(post_id):
    post = db.session.get(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for('show_post', post_id=post.id))
    return render_template('make-post.html', form=edit_form)


@app.route('/delete/<int:post_id>')
@admin_only
def delete_post(post_id):
    post_to_delete = db.session.get(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == '__main__':
    app.run(debug=True)
