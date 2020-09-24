from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Regexp, Length
from wtforms import ValidationError
from flask_wtf.file import FileField,FileAllowed

from flask_login import current_user
from mathsclinicblog.models import User

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(message = "This field cannot be empty"),
    Email(message = "Please enter a valid email address")])
    password = PasswordField('Password',validators=[DataRequired(message = "This field cannot be empty")])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(message = "This field cannot be empty"),
    Email(message = "Please enter a valid email address")])
    about_me = TextAreaField('About me')
    username = StringField('Username', validators=[DataRequired(message = "This field cannot be empty"), 
    Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, '
               'numbers, dots or underscores')])
    password = PasswordField('Password',validators=[DataRequired(message = "This field cannot be empty"),
    EqualTo('pass_confirm',message='Passwords must match!')])
    age = SelectField('Age',
                             choices=[('<10 years', 'Less than 10 years'),
                                      ('10-15years', '10 - l5years'),
                                      ('15-20years', '15 - 20years'), ('>20 years', 'Greater than 20 years')],
                             validators=[DataRequired(message = "This ffield cannot be empty.")])
    class_name =SelectField('Educational Level',
                             choices=[('Primary', 'Basic School'),
                                      ('Junior Sec', 'Junior Secondary School'),
                                      ('Senior Sec', 'Senior Secondary School'), ('Tertiary', 'Higher Institution'), 
                                      ('others', 'others')],
                                      
                             validators=[DataRequired(message = "This field cannot be empty")]) 
    pass_confirm = PasswordField('Confirm Password',validators=[DataRequired(message = "This field cannot be empty.")])
    submit = SubmitField('Register!')

    def check_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Your email has been registered already!')

    def check_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Your username has been registered already!')


class UpdateUserForm(FlaskForm):

    email = StringField('Email',validators=[DataRequired(),Email()])
    about_me = TextAreaField('About me')
    username = StringField('Username', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, '
               'numbers, dots or underscores')])
    age = SelectField('Update Age',
                             choices=[('< 10years','Less than 10 years'),
                                      ('10-15years','10 - l5years'),
                                      ('15-20years','15 - 20years'), ('>20 years','Greater than 20 years')],
                             validators=[DataRequired()])
    class_name =SelectField('Educational Level',
                             choices=[('Primary', 'Basic School'),
                                      ('Junior Sec', 'Junior Secondary School'),
                                      ('Senior Sec', 'Senior Secondary School'), ('Tertiary', 'Higher Institution'), 
                                      ('others', 'others')],
                                      
                             validators=[DataRequired(message = "This field cannot be empty")]) 
    
    picture = FileField('Update Profile Picture',validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')




    def check_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Your email has been registered already!')

    def check_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Your username has been registered already!')



class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[
    DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')

class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')