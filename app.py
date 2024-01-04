from flask import Flask, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.route('/')
def home_page():
    if 'username' not in session:
        flash('Please login first!', 'danger')
        return redirect('/login')
    else:
        return redirect(f'/users/{session["username"]}')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Register user: produce form & handle form submission"""
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        try:
            user = User.register(username, password, email, first_name, last_name)
            db.session.add(user)
            db.session.commit()
            session['username'] = user.username
            flash('Welcome! Successfully Created Your Account!', 'success')
            return redirect(f'/users/{user.username}')
        except IntegrityError:
            form.username.errors.append('Username taken. Please pick another')
            return render_template('register.html', form=form)
    else:
        return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Produce login form or handle login"""
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            flash(f'Welcome Back, {user.username}!', 'primary')
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password']
            return render_template('login.html', form=form)
    else:
        return render_template('login.html', form=form)

@app.route('/secret')
def show_secret():
    """Show secret page if user is logged in"""
    if 'username' not in session:
        flash('Please login first!', 'danger')
        return redirect('/login')
    else:
        return render_template('secret.html')

@app.route('/logout')
def logout_user():
    """Logout user"""
    session.pop('username')
    flash('Goodbye!', 'info')
    return redirect('/login')

@app.route('/users/<username>')
def show_user(username):
    """Show user info"""
    if 'username' not in session:
        flash('Please login first!', 'danger')
        return redirect('/login')
    else:
        form = FeedbackForm()
        user = User.query.get_or_404(username)
        return render_template('user.html', user=user, form=form)

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """Delete user"""
    if 'username' not in session:
        flash('Please login first!', 'danger')
        return redirect('/login')
    else:
        user = User.query.get_or_404(username)
        db.session.delete(user)
        db.session.commit()
        session.pop('username')
        flash('User deleted', 'info')
        return redirect('/login')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    """Add feedback"""
    if 'username' not in session:
        flash('Please login first!', 'danger')
        return redirect('/login')
    else:
        form = FeedbackForm()
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            feedback = Feedback(title=title, content=content, username=username)
            db.session.add(feedback)
            db.session.commit()
            flash('Feedback added!', 'success')
            return redirect(f'/users/{username}')
        else:
            return redirect(f'/users/{username}')

@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    """Delete feedback"""
    if 'username' not in session:
        flash('Please login first!', 'danger')
        return redirect('/login')
    else:
        feedback = Feedback.query.get_or_404(feedback_id)
        db.session.delete(feedback)
        db.session.commit()
        flash('Feedback deleted', 'info')
        return redirect(f'/users/{feedback.username}')

@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    """Update feedback"""
    if 'username' not in session:
        flash('Please login first!', 'danger')
        return redirect('/login')
    else:
        feedback = Feedback.query.get_or_404(feedback_id)
        form = FeedbackForm(obj=feedback)
        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.commit()
            flash('Feedback updated!', 'success')
            return redirect(f'/users/{feedback.username}')
        else:
            return render_template('feedback.html', form=form, feedback=feedback)