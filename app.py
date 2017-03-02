from flask import (Flask, g, render_template, flash, redirect, url_for, abort)

import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'LgD*&FhlbvdgGfOGH8uif7iFHGPIpuipu9r9rY`afdgG^&TO*)U*PYjsigrO'


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    # g.user = current_user


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


@app.route('/entries/<slug>')
@app.route('/details/<slug>')
def details(slug=None):
    if slug:
        # get the entry to display
        entry = (models.Task.select()
                 .where(models.Task.title == slug.replace('_', ' ')))
        if entry.count() == 0:
            abort(404)
        return render_template('detail.html', entry=entry.get())
    else:
        # Redirect to index if no slug provided
        return redirect(url_for('index'))


@app.route('/entry', methods=('GET', 'POST'))
@app.route('/entry/<slug>', methods=('GET', 'POST'))
@app.route('/entries/edit/<slug>', methods=('GET', 'POST'))
def entry(slug=None):
    form = forms.NewForm()
    if slug:
        # edit entry
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
            return redirect(url_for('index'))
        if form.id.data == 0:
            # populate from data
            form.id.data = form_data.id
            form.title.data = form_data.title
            form.date.data = form_data.date
            form.time_spent.data = form_data.time_spent
            form.what_i_learned.data = form_data.what_i_learned
            form.resources_to_remember.data = form_data.resources_to_remember
    else:
        # new entry
        if form.validate_on_submit():
            models.Task.create(
                title=form.title.data,
                date=form.date.data,
                time_spent=form.time_spent.data,
                what_i_learned=form.what_i_learned.data,
                resources_to_remember=form.resources_to_remember.data
            )
            return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/entries/delete/<slug>', methods=('GET', 'POST'))
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
    return redirect(url_for('index'))

if __name__ == '__main__':
    models.initialize()
    app.run(debug=DEBUG, host=HOST, port=PORT)
