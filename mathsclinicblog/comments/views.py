from flask import jsonify, request, g, url_for, current_app, Blueprint
from flask_login import current_user,login_required
from mathsclinicblog import db
from mathsclinicblog.models import BlogPost, Comment, Permission
from mathsclinicblog.comments.forms import CommentForm
from mathsclinicblog.decorator import permission_required

comments_page = Blueprint('comments_page',__name__)


@comments_page.route('/<int:comment_id>')
def get_comment():
    comment = Comment.query.get_or_404(comment_id) #the id column sould give us the comment id
    post = BlogPost.query.get_or_404(id)
    return render_template('comment.html',body=comment.body,
                            date=comment.timestamp,post=post
    )

@comments_page.route('/create_comment',methods=['GET','POST'])
@login_required
def create_comment():
    form = CommentForm()

    if form.validate_on_submit():

        comment_post = Comment(body=form.body.data,
                            post_id=posts.id,
                            user_id=current_user.id
                            )
        post.comments = post.comments + 1
        db.session.add(comment_post)
        db.session.commit()
        flash('comment Created')
        return redirect(url_for('blog_posts.blog_post'))

    return render_template('create_comment.html',form=form)


