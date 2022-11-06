from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, LoginManager, UserMixin, login_required, current_user
from datetime import datetime
import os


base_dir = os.path.dirname(os.path.realpath(__file__))

# create the app 
app = Flask(__name__)

# configure the SQLite database 
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(base_dir, 'my_blog.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = 'dhduik46275bceb98bf55e21c'

# create the extension 
db = SQLAlchemy(app)

login_manager = LoginManager(app)

db.init_app(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(255), nullable=False, unique=True)
    last_name = db.Column(db.String(255), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    gender = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)


    def __repr__(self) -> str:
        return f"user{self.first_name}"

class Post(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    content = db.Column(db.String(255), nullable=False, unique=True)
    author = db.Column(db.String, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    
    def __repr__(self) -> str:
        return f"user {self.title}"

class Message(db.Model):
    # __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String, nullable=False)
    

    def __repr__(self):
        return f"Message: <{self.title}>"


@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))

@app.route("/")
def home():
    posts = Post.query.all()

    return render_template("index.html", posts=posts)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        sender = request.form.get('name')
        email = request.form.get('email')
        phone_number = request.form.get('phonenumber')
        message = request.form.get('message')

        new_message = Message(sender=sender, email=email, phone_number=phone_number, message=message)
        db.session.add(new_message)
        db.session.commit()

        flash("Message sent successfully.")
        return redirect(url_for('home'))

    return render_template('contact.html')

# creating route 
@app.route('/create', methods=['GET', 'POST'])
def create():

    if request.method == "POST":
        title= request.form.get('title')
        content= request.form.get('message')
        author = current_user.username

        title_exist = Post.query.filter_by(title=title).first()
        if title_exist:
            return redirect(url_for("create"))

        content_exist = Post.query.filter_by(content=content).first()
        if content_exist:
            return redirect(url_for("create"))
        new_post= Post(title=title, content=content, author=author)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('create'))

    return render_template("create.html")

# Update route
@login_required
@app.route('/update/<int:id>/', methods=['GET', 'POST'])
def update(id):
    edit_user= Post.query.get_or_404(id)

    if request.method == 'POST':
        edit_user.title= request.form.get('title')
        edit_user.content= request.form.get('message')

        db.session.commit()
        flash("Your changes have been saved.")

        return redirect(url_for('home'))
    
    
    return render_template('update.html', edit_user=edit_user)


@app.route('/blog/<int:id>')
def blog(id):
    pick_blog = Post.query.filter_by(id=id).first()
    return render_template('blog.html', pick_blog=pick_blog)

# about route 
@app.route('/about')
def about():

    return render_template('about.html')

# delete route 
@login_required
@app.route('/delete/<int:id>/', methods=['GET'])
def delete_post(id):
    post_to_delete = Post.query.get_or_404(id)

    db.session.delete(post_to_delete)
    db.session.commit()
    flash("That article has been deleted!")
    return redirect(url_for('home'))


# creating a logout 
@app.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('home'))

# creating a login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        login_user(user)
        flash("You are now logged in.")
        return redirect(url_for('home',id=user.id))

    return render_template('login.html')


# creating a signup 
@app.route('/signup', methods=["POST","GET"])
def signup():
    if request.method == "POST":
        first_name = request.form.get("firstname")
        last_name = request.form.get("lastname")
        email = request.form.get("email")
        username = request.form.get('username')
        gender = request.form.get("gender")
        password = request.form.get("password")

        first_name_exist = User.query.filter_by(first_name=first_name).first()
        if first_name_exist:
            return redirect(url_for("signup"))

        last_name_exist = User.query.filter_by(last_name=last_name).first()
        if last_name_exist:
            return redirect(url_for("signup"))

        username_exists = User.query.filter_by(username=username).first()
        if username_exists:
            return redirect(url_for('register'))

        email_exist = User.query.filter_by(email=email).first()
        if email_exist:
            return redirect(url_for("signup"))
        
        password_hash = generate_password_hash(password)
        
        new_user= User(first_name=first_name,last_name=last_name, username=username, email=email, gender=gender, password_hash=password_hash)
        with app.app_context():
            db.session.add(new_user)
            db.session.commit()
        return redirect(url_for("login"))

    return render_template("signup.html")


if __name__ == "__main__":
    app.run(debug=True)
