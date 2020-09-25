# blog_posts/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField
from wtforms.validators import DataRequired
from flask_pagedown.fields import PageDownField

class BlogPostForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired()])
    text = PageDownField('Text',validators=[DataRequired()])
    submit = SubmitField("Post")
