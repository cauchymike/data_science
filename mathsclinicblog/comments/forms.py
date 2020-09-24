from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField,\
    SubmitField
from wtforms.validators import DataRequired



class CommentForm(FlaskForm):
    body = TextAreaField('Enter your comment', validators=[DataRequired()])
    submit = SubmitField('Submit')
