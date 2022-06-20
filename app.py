from crypt import methods
from flask import Flask, request, render_template, redirect, session, flash
from models import connect_db, db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)

@app.route('/')
def redirect_register():
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        db.session.commit()
        session["user_id"] = new_user.username
        return redirect(f"/users/{new_user.username}")
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session["user_id"] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ["Invalid username/password"]
    return render_template('login.html', form=form)

@app.route('/users/<username>')
def show_secret(username):
    if "user_id" not in session:
        return redirect('/login')
    user = User.query.get_or_404(username)
    return render_template('user.html', user=user)

@app.route('/logout')
def logout_user():
    session.pop('user_id')
    return redirect('/')

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    if session["user_id"] != username:
        return redirect('/')
    session.pop('user_id')
    user = User.query.get_or_404(username)
    for feedback in user.feedback:
        db.session.delete(feedback)
        db.session.commit()
    db.session.delete(user)
    db.session.commit()
    return redirect('/')

@app.route('/users/<username>/feedback/add', methods=["GET", 'POST'])
def add_feedback(username):
    if session["user_id"] != username:
        return redirect('/')
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        new_feedback = Feedback(title=title, content=content, username=username)

        db.session.add(new_feedback)
        db.session.commit()
        return redirect(f'/users/{username}')
    return render_template('add_feedback.html', form=form)

@app.route('/feedback/<int:id>/update', methods=["GET", "POST"])
def update_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    if session["user_id"] != feedback.username:
        return redirect('/')
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        feedback.title = title
        feedback.content = content

        db.session.commit()
        return redirect(f'/users/{feedback.username}')
    return render_template('edit_feedback.html', feedback=feedback, form=form)

@app.route('/feedback/<int:id>/delete', methods=["POST"])
def delete_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    if session["user_id"] != feedback.username:
        return redirect('/')
    db.session.delete(feedback)
    db.session.commit()
    return redirect(f'/users/{feedback.username}')