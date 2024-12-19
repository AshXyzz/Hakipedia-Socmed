from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import User, Post, Like, Comment, Dislike, ReplyComment, CommentLike
from . import db
from sqlalchemy import desc, and_, or_ # can descending order the oder_by database. or_ is for multiple search termers


views = Blueprint('views', __name__)
months = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}

@views.route('/home/', methods=['GET','POST'])
@login_required 
def home():
    posts = db.session.query(Post, User).join(User, Post.user_id == User.id).order_by(Post.date.desc()).limit(10).all()
    if request.method == "POST":
        if request.form.get("search") != None:
            search = request.form.get('search')
            return redirect(url_for("views.search", search=search))
    else:
        return render_template("home.html", user=current_user, page="Home", posts=posts, current_user=current_user)


@views.route('/profile/') # redirect you to your own profile
@login_required
def profile_redirect():
    return redirect('/profile/%s' % current_user.id)

@views.route('/profile/<int:id>', methods=["GET","POST"])
@login_required
def user_profile(id):
    if request.method == "GET":
        # try:
        user = User.query.get(id)
        posts = Post.query.filter_by(user_id=id).order_by(Post.date.desc()).limit(5).all()

        name = user.first_name + " " + user.last_name
        pagename = name + "'s Profile"
        date_joined = str(user.date_joined).split(" ")[0] # date_joined = the "2023-06-11 12:34:56" but split at the space, and only take the first value of the list.
        date_joined_list = date_joined.split("-")
        year = date_joined_list[0]
        if date_joined_list[1][0] == "0":
            string = date_joined_list[1][1:]
            month = months.get(int(string))
        else:
            month = months.get(date_joined_list[1])
        day = date_joined_list[2]
        date_joined = str(month) + " " + str(day) + ", " + str(year)


        return render_template("user_profile.html", page=pagename, name=name, user=user, id=int(id), date_joined=date_joined, posts=posts, current_user=current_user)
        # except Exception as e:
        #     return render_template("404.html", page="Error 404 Not Found", error="The user you are looking for doesn't exist.", user=current_user)
    elif request.method == "POST":
        if request.form.get("post") != None:
            post = request.form.get("post")
            title = request.form.get('title')
            new_post = Post(data=post, user_id=current_user.id, title=title)
            db.session.add(new_post)
            db.session.commit()
            
            return redirect('/profile/%s' % id)
        

@views.route('/edit/profile/')
@login_required
def redirect_to_edit_profile():
    return redirect("/edit/profile/%s" % current_user.id)

@views.route('/post/<int:id>', methods=['GET','POST'])
@login_required
def view_post(id):

    previous_page = request.referrer
    post = Post.query.get(id)
    user = User.query.get(post.user_id)

    
    like = Like.query.filter_by(user=current_user, post=post).first()
    liked = like

    dislike = Dislike.query.filter_by(user=current_user, post=post).first()
    disliked = dislike

    comments = Comment.query.filter_by(post=post).order_by(Comment.date.desc()).all()


    date = str(post.date).split(" ")[0]



    try:
        return render_template("view_post.html", page="Post", user=user, post=post, current_user=current_user, liked=liked, comments=comments, date=date, disliked=disliked)
    except Exception as e:
        print(e)
        return render_template("404.html", error="This post doesn't exist.", user=user, current_user=current_user)


@views.route('/delete/post/<int:id>')
@login_required
def delete_post(id):
    post = Post.query.get(id)
    previous_page = request.referrer
    if id == None:
        flash("You can only delete your own posts.", category="error")
        return redirect(url_for("views.home"))
    else:
        try:
            if int(current_user.id) == int(post.user_id):
                db.session.delete(post)
                db.session.commit()
                flash("Post deleted.", category="success")
                return redirect("/profile/")
            else: # this is actually unneeded because flask automatically sets the post to None if it's not the user's post, so that's why we have try and except.
                flash("You can only delete your own posts.", category="error")
                return redirect("/profile/")
        except Exception as e:
            flash("You can only delete your own posts.", category="error")
            print(e)
            return redirect(url_for("views.home"))
        
@views.route('/search/')
@login_required
def empty_search_handler():
    previous_page = request.referrer
    return redirect(previous_page)

@views.route("/search/<search>", methods=['GET','POST'])
@login_required
def search(search):
    if request.method == "POST":
        if request.form.get("search") != None:
            search = request.form.get('search')
            return redirect("/search/%s" % search)
    else:
        # posts = Post.query.filter(Post.data.ilike(f"%{search}%")).all()
        posts = db.session.query(Post, User).join(User, Post.user_id == User.id).filter(
            or_(Post.data.ilike(f"%{search}%"), Post.title.ilike(f"%{search}%"))).all()
        # users = User.query.filter(User.first_name.ilike(f"%{search}%")).all()
        full_name = User.first_name + " " + User.last_name
        if len(search) > 2: # to make sure all the users don't show up from something like search term "a"
            users = User.query.filter(
                or_(User.first_name.ilike(f"%{search}%"), User.last_name.ilike(f"%{search}%"), full_name.ilike(f"%{search}%"))).all()
        else:
            users = None
        


        return render_template('search.html', posts=posts, users=users, query=search, user=current_user, current_user=current_user, page="Search")
    
@views.route('/post/<int:post_id>/like', methods=["POST"])
@login_required
def like_post(post_id):
    previous_page = request.referrer
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user=current_user, post=post).first()
    # make sure they can't dislike and like
    dislike = Dislike.query.filter_by(user=current_user, post=post).first()
    #check if the current user has already liked the post
    if like:
        # user has already liked the post, so we'll remove the like
        db.session.delete(like)
    else:
        if dislike: # make sure they can't dislike and like
            db.session.delete(dislike)
        # user hasn't liked the post, so we'll add a like
        like = Like(user=current_user, post=post)
        db.session.add(like)
    db.session.commit()
    
    return redirect(previous_page)

@views.route('/post/<int:post_id>/dislike', methods=["POST"])
@login_required
def dislike_post(post_id):
    previous_page = request.referrer
    post = Post.query.get_or_404(post_id)
    dislike = Dislike.query.filter_by(user=current_user, post=post).first()
    # we want to make sure that if they dislike it when they already liked it, the like is removed and replaced.
    like = Like.query.filter_by(user=current_user, post=post).first()
    #check if already disliked by current user
    if dislike:
        db.session.delete(dislike)
    else:
        if like: # make sure they can't dislike and like
            # user has already liked the post, so we'll remove the like
            db.session.delete(like)
        dislike = Dislike(user=current_user, post=post)
        db.session.add(dislike)

    db.session.commit()

    return redirect(previous_page)

@views.route("/post/<int:post_id>/comment/<int:comment_id>/like", methods=["POST"])
@login_required
def like_comment(post_id, comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post = Post.query.get_or_404(post_id)
    comment_like = CommentLike.query.filter_by(user=current_user, comment=comment).first()

    if comment_like:
        db.session.delete(comment_like)
    else:
        comment_like = CommentLike(user=current_user, comment=comment, post=post)
        db.session.add(comment_like)
    db.session.commit()

    return redirect(request.referrer)

@views.route('/post/<int:id>/comment/', methods=["POST"])
@login_required
def comment_on_post(id):
    comment_data = request.form.get("comment")
    post = Post.query.get(id)

    comment = Comment(user=current_user, data=comment_data, post=post)
    db.session.add(comment)
    db.session.commit()


    return redirect(request.referrer)

@views.route('/delete/comment/<int:id>')
@login_required
def delete_comment(id):
    comment = Comment.query.get(id)
    if id == None:
        flash("You can only delete your own comments.", category="error")
        return redirect(url_for("views.home"))
    else:
        try:
            if int(current_user.id) == int(comment.user_id):
                db.session.delete(comment)
                db.session.commit()
                flash("Comment deleted.", category="success")
                return redirect(request.referrer)
            else: #technically uneeded. (See delete_post())
                flash("You can only delete your own comments.", category="error")
                return redirect(request.referrer)
        except Exception as e:
            flash("You can only delete your own posts.", category="error")
            print(e)
            return redirect(request.referrer)
        

@views.route('/comment/<int:id>/reply/', methods=["POST"])
@login_required
def reply_to_comment(id):
    reply_data = request.form.get("reply")
    print(reply_data)
    comment = Comment.query.get(id)

    reply = ReplyComment(user=current_user, data=reply_data, comment=comment)
    db.session.add(reply)
    db.session.commit()

    flash("Reply added.", category='success')

    return redirect(request.referrer)


@views.route('/delete/reply/<int:id>/')
@login_required
def delete_reply(id):
    reply = ReplyComment.query.get(id)
    if id == None:
        flash("You can only delete your own replies.", category='error')
        return redirect(url_for('views.home'))
    else:
        try:
            if int(current_user.id) == int(reply.user_id):
                db.session.delete(reply)
                db.session.commit()
                flash("Reply deleted.", category='success')
                return redirect(request.referrer)
            else: # technically unneeded. (see delete_post())
                flash("You can only delete your own replies.", category='error')
                return redirect(request.referrer)
        except Exception as e:
            flash("You can only delete your own replies.", category='error')
            print(e)
            return redirect(request.referrer)