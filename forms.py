from flask_wtf import FlaskForm
from wtforms import (StringField, DateField, IntegerField, TextAreaField,
                     HiddenField, PasswordField)
from wtforms.validators import (DataRequired, Length, NumberRange,
                                ValidationError)

import datetime

from models import Task


def title_exists(form, field):
    if Task.select().where((Task.id != form.id.data) &
                           (Task.title == field.data)).exists():
        raise ValidationError('An entry with this title already exists.')


class NewForm(FlaskForm):
    id = HiddenField(
        '',
        default=0
        )
    title = StringField(
        'Title',
        validators=[
            DataRequired(),
            Length(min=2),
            title_exists
        ])
    date = DateField(
        'Date (YYYY-MM-DD)',
        format="%Y-%m-%d",
        default=datetime.date.today,
        validators=[
            DataRequired()
        ])
    time_spent = IntegerField(
        'Time Spent (Hours)',
        validators=[
            NumberRange(min=0)
        ])
    what_i_learned = TextAreaField(
        'What I Learned',
        validators=[DataRequired()]
    )
    resources_to_remember = TextAreaField(
        'Resources to Remember',
        validators=[DataRequired()]
    )
    tags = StringField(
        'Tags (separate with commas)'
    )


class LoginForm(FlaskForm):
    username = StringField('User Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
