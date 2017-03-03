from flask import Flask, g, render_template, redirect, url_for, abort, flash
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)

import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'LgD*&FhlbvdgGfOGH8uif7iFHGPIpuipu9r9rY`afdgG^&TO*)U*PYjsigrO'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


def add_tags(task, data):
    """ Remove existing tags and save new tags for task """
    query = models.Tags.delete().where(models.Tags.task == task)
    query.execute()
    # Insert the new tags
    for my_tag in data.split(","):
        # Try insert to tags table
        try:
            models.Tags.create(
                name=my_tag.strip().lower(),
                task=task
            )
        except models.IntegrityError:
            # Already in table
            pass


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.username == form.username.data)
        except models.DoesNotExist:
            form.username.data = ""
            flash("Invalid User Name & Password combination")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You Have successfully logged in")
                return redirect(url_for('index'))
            else:
                form.username.data = ""
                flash("Invalid User Name & Password combination")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have successfully logged out")
    return redirect(url_for('index'))


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


@app.route('/')
@app.route('/entries')
def index():
    # get the list to display
    entries = models.Task.select()
    return render_template('index.html', entries=entries)


@app.route('/entries/tags/<slug>')
def tags(slug=None):
    if slug:
        # get the list to display
        entries = (models.Task.select().join(models.Tags)
                   .where(models.Tags.name == slug))
        return render_template('index.html', entries=entries, tag=slug)
    else:
        # Redirect to index if no slug provided
        return redirect(url_for('index'))


@app.route('/entries/<slug>')
@app.route('/details/<slug>')
def details(slug=None):
    if slug:
        # get the entry to display
        entry = (models.Task.select()
                 .where(models.Task.title == slug.replace('_', ' ')))
        if entry.count() == 0:
            abort(404)
        # Get the tags for the task
        return render_template('detail.html', entry=entry.get())
    else:
        # Redirect to index if no slug provided
        return redirect(url_for('index'))


@app.route('/entry', methods=('GET', 'POST'))
@app.route('/entry/<slug>', methods=('GET', 'POST'))
@app.route('/entries/edit/<slug>', methods=('GET', 'POST'))
@login_required
def entry(slug=None):
    form = forms.NewForm()
    if slug:
        # Get the Task data
        entry = (models.Task.select()
                 .where(models.Task.title == slug.replace('_', ' ')))

        if entry.count() == 0:
            # invalid slug
            abort(404)
        form_data = entry.get()
        if form.validate_on_submit():
            # data submitted & valid
            form_data.title = form.title.data
            form_data.date = form.date.data
            form_data.time_spent = form.time_spent.data
            form_data.what_i_learned = form.what_i_learned.data
            form_data.resources_to_remember = form.resources_to_remember.data
            form_data.save()
            add_tags(form_data, form.tags.data)
            flash("Entry Updated")
            return redirect(url_for('index'))
        if form.id.data == 0:
            # populate from data
            form.id.data = form_data.id
            form.title.data = form_data.title
            form.date.data = form_data.date
            form.time_spent.data = form_data.time_spent
            form.what_i_learned.data = form_data.what_i_learned
            form.resources_to_remember.data = form_data.resources_to_remember
            alltags = []
            for tag in form_data.get_tags():
                alltags.append(tag.name)
            form.tags.data = ", ".join(alltags)
        if form.errors:
            flash("Not saved, please see errors below")
    else:
        # New Task
        if form.validate_on_submit():
            task = models.Task.create(
                title=form.title.data,
                date=form.date.data,
                time_spent=form.time_spent.data,
                what_i_learned=form.what_i_learned.data,
                resources_to_remember=form.resources_to_remember.data
            )
            # Add Tags
            add_tags(task, form.tags.data)
            flash("New entry saved.")
            return redirect(url_for('index'))
        if form.errors:
            flash("Not saved, please see errors below")
    return render_template('new.html', form=form)


@app.route('/entries/delete/<slug>', methods=('GET', 'POST'))
@login_required
def delete(slug=None):
    if slug:
        # delete entry
        try:
            (models.Task.select()
             .where(models.Task.title == slug.replace('_', ' '))
             .get().delete_instance())
        except models.DoesNotExist:
            # do nothing as user will just go back to index
            pass
    flash("Entry deleated")
    return redirect(url_for('index'))

if __name__ == '__main__':
    models.initialize()
    try:
        models.User.new(
            username='admin',
            password='1234'
        )
    except ValueError:
        # Do nothing as user is already entered
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)
