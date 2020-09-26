from flask import render_template,url_for,flash,redirect,request,Blueprint, abort, Response
from flask_login import login_user, current_user, logout_user, login_required
from mathsclinicblog import db
from mathsclinicblog.models import User, BlogPost
from mathsclinicblog.users.forms import RegistrationForm,LoginForm,UpdateUserForm, PasswordResetForm,PasswordResetRequestForm
from mathsclinicblog.users.picture_handler import add_profile_pic
from flask import send_from_directory, send_file
import boto3
import os
from mathsclinicblog import app
from mathsclinicblog.s3_storage import upload_file, list_files, download_file
from mathsclinicblog.email import send_email
from mathsclinicblog.resourses import get_bucket, get_buckets_list
from mathsclinicblog.filters import datetimeformat, file_type

users = Blueprint('users',__name__)


@users.before_app_request  #registers a function that runs before the view function
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint and request.blueprint != 'users':
                #and request.endpoint != 'static':
            return redirect(url_for('users.unconfirmed'))#end point is users.unconfirmed
        
@users.route('/pygments.css')
        def pygments_css():
            return pygments_style_defs('tango'), 200, {'Content-Type': 'text/css'}


@users.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect('core.index')
    return render_template('unconfirmed.html')

# register
@users.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data,
                    age = form.age.data,
                    about_me = form.about_me.data,
                    class_name = form.class_name.data)

        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        #link = 
        #send_mail (user.email, link, user = user, token = token)
        send_email(user.email,'Confirm Your Account',
        '/email/confirm', user = user, token= token )
        flash('A confirmation email has been sent to your email address.')
        return redirect(url_for('core.index'))#instead of going to the login page, we send them to homepage
        #return redirect(url_for('users.login'))

    return render_template('register.html',form=form)


@users.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('core.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')    
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('core.index'))


@users.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
   
    send_email(current_user.email, 'Confirm Your Account',
              '/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('core.index'))





# login
@users.route('/login',methods=['GET','POST'])
def login():

    form = LoginForm()
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()
        
        if user.check_password(form.password.data) and user is not None:

            login_user(user)
            flash('Log in Success!')

            next = request.args.get('next')

            if next == None or not next[0]=='/':
                next = url_for('core.index')

            return redirect(next)

    return render_template('login.html',form=form)

@users.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('core.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        #once the form validates, we query the database for the email submitted.
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       '/email/reset_password',
                       user=user, token=token)
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('core.index'))
    return render_template('reset_password_request.html', form=form)


@users.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):#i just found out that we call the name of the fuction when referring to our endpoint
    if not current_user.is_anonymous:
        return redirect(url_for('core.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('users.login'))
        else:
            return redirect(url_for('core.index'))
    return render_template('reset_password.html', form=form)






# logout
@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("core.index"))


# account (update UserForm)
@users.route('/account',methods=['GET','POST'])
@login_required
def account():

    form = UpdateUserForm()
    if form.validate_on_submit():

        #if form.picture.data:
         #   username = current_user.username
          #  pic = add_profile_pic(form.picture.data,username)
           # current_user.profile_image = pic
            

        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.age = form.age.data
        current_user.class_name = form.class_name.data
        current_user.about_me =form.about_me.data
        db.session.commit()
        flash('User Account Updated!')
        return redirect(url_for('users.account'))

    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    #
    return render_template('account.html',form=form)

@users.route('/upload_ds', methods=['POST'])
@login_required
def upload():
    file = request.files['file']

    my_bucket = get_bucket()
    my_bucket.Object(file.filename).put(Body=file)

    flash('File uploaded successfully')
    return redirect(url_for('users.storage_ds'))


@users.route('/storage_ds')
@login_required
def storage_ds():
    #my_bucket = get_bucket()
    #summaries = my_bucket.objects.all()
    my_bucket = get_bucket()
    summaries_1 = []
    for obj_white in my_bucket.objects.filter(Prefix = "data_science/"):
        summaries_1.append(obj_white)
    return render_template('data_science.html', my_bucket = my_bucket, contents_ds = summaries_1)

    


@users.route("/download_ds", methods=['POST'])
@login_required
def download_ds():
    key = request.form['key']

    my_bucket = get_bucket()
    file_obj = my_bucket.Object(key).get()

    return Response(
        file_obj['Body'].read(),
        mimetype='application/pdf',
        headers={"Content-Disposition": "attachment;filename={}".format(key)}
    )

@users.route('/upload_basic', methods=['POST'])
@login_required
def upload_basic():
    file = request.files['file']

    my_bucket = get_bucket()
    my_bucket.Object(file.filename).put(Body=file)

    flash('File uploaded successfully')
    return redirect(url_for('users.storage_basic'))


@users.route('/storage_basic')
@login_required
def storage_basic():
    #my_bucket = get_bucket()
    #summaries = my_bucket.objects.all()
    my_bucket = get_bucket()
    summaries_2 = []
    for obj_white in my_bucket.objects.filter(Prefix = "basic_school/"):
        summaries_2.append(obj_white)
    return render_template('basic_sch.html', my_bucket = my_bucket, contents_basic = summaries_2)

    


@users.route("/download_basic", methods=['POST'])
@login_required
def download_basic():
    key = request.form['key']

    my_bucket = get_bucket()
    file_obj = my_bucket.Object(key).get()

    return Response(
        file_obj['Body'].read(),
        mimetype='application/pdf',
        headers={"Content-Disposition": "attachment;filename={}".format(key)}
    )

@users.route('/upload_junior', methods=['POST'])
@login_required
def upload_junior():
    file = request.files['file']

    my_bucket = get_bucket()
    my_bucket.Object(file.filename).put(Body=file)

    flash('File uploaded successfully')
    return redirect(url_for('users.storage_junior'))


@users.route('/storage_junior')
@login_required
def storage_junior():
    #my_bucket = get_bucket()
    #summaries = my_bucket.objects.all()
    my_bucket = get_bucket()
    summaries_3 = []
    for obj_white in my_bucket.objects.filter(Prefix = "junior_school/"):
        summaries_3.append(obj_white)
    return render_template('junior_sec.html', my_bucket = my_bucket, contents_junior = summaries_3)

    


@users.route("/download_junior", methods=['POST'])
@login_required
def download_junior():
    key = request.form['key']

    my_bucket = get_bucket()
    file_obj = my_bucket.Object(key).get()

    return Response(
        file_obj['Body'].read(),
        mimetype='application/pdf',
        headers={"Content-Disposition": "attachment;filename={}".format(key)}
    )


@users.route('/upload_senior', methods=['POST'])
@login_required
def upload_senior():
    file = request.files['file']

    my_bucket = get_bucket()
    my_bucket.Object(file.filename).put(Body=file)

    flash('File uploaded successfully')
    return redirect(url_for('users.storage_senior'))


@users.route('/storage_senior')
@login_required
def storage_senior():
    #my_bucket = get_bucket()
    #summaries = my_bucket.objects.all()
    my_bucket = get_bucket()
    summaries_4 = []
    for obj_white in my_bucket.objects.filter(Prefix = "senior_school/"):
        summaries_4.append(obj_white)
    return render_template('junior_sec.html', my_bucket = my_bucket, contents_senior = summaries_4)

    


@users.route("/download_senior", methods=['POST'])
@login_required
def download_senior():
    key = request.form['key']

    my_bucket = get_bucket()
    file_obj = my_bucket.Object(key).get()

    return Response(
        file_obj['Body'].read(),
        mimetype='application/pdf',
        headers={"Content-Disposition": "attachment;filename={}".format(key)}
    )





    





# user's list of Blog posts
@users.route("/<username>")
def user_posts(username):
    page = request.args.get('page',1,type=int)
    user = User.query.filter_by(username=username).first_or_404()
    blog_posts = BlogPost.query.filter_by(author=user).order_by(BlogPost.date.desc()).paginate(page=page,per_page=5)
    #comments = Comment.query.filter_by(user_comment = user).order_by(Comment.timestamp.desc()).paginate(page=page,per_page=5)
    return render_template('user_blog_posts.html',blog_posts=blog_posts,user=user)

