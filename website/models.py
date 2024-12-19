from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Post(db.Model):  # telling it what all posts need to look like.
    # primary key is the unique identifier for each database "entry", each user has their own (although they don't know it)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    data = db.Column(db.String(10000))
    # func function automatically gets the time they put it in
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    # saying the type of column is integer, foreign key means you must pass a valid id of an existing user to this column (one user that has many posts, one-to-many relationship)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    likes = db.relationship("Like", backref="post",
                            cascade="all, delete-orphan")
    dislikes = db.relationship(
        "Dislike", backref="post", cascade="all, delete-orphan")
    comments = db.relationship(
        "Comment", backref='post', cascade='all, delete-orphan')
    comment_likes = db.relationship(
        "CommentLike", backref='post', cascade='all, delete-orphan')
    replies = db.relationship(
        "ReplyComment", backref='post', cascade='all, delete-orphan')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)  # 150 is max length
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    profile_picture = db.Column(
        db.String(1000), default="default_profile_photo.jpg")
    # every time the user creates a post, add into this user-posts relationship the id of the post.
    posts = db.relationship("Post", backref='user',
                            cascade='all, delete-orphan')
    bio = db.Column(db.String(1500))
    links = db.Column(db.String(500))
    # func function automatically gets the time they put it in
    date_joined = db.Column(db.DateTime(timezone=True), default=func.now())
    # backref argument creates a reverse reference from this model back to the User and Post models. Cascade argument specifies te cascading behavior for the relationship when performing operations such as deleting a user or post. All means that all operations on the parent object will be cascaded to the regular objects. delete-orphan means that when a parent object is deleted, any orphaned child objects (Likes) will also be deleted.
    likes = db.relationship("Like", backref="user",
                            cascade="all, delete-orphan")
    dislikes = db.relationship(
        "Dislike", backref='user', cascade='all, delete-orphan')
    comment_likes = db.relationship(
        "CommentLike", backref='user', cascade='all, delete-orphan')
    comments = db.relationship(
        "Comment", backref='user', cascade='all, delete-orphan')
    replies = db.relationship(
        "ReplyComment", backref="user", cascade='all, delete-orphan')


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class Dislike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(1000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    replies = db.relationship(
        "ReplyComment", backref='comment', cascade='all, delete-orphan')
    comment_likes = db.relationship(
        "CommentLike", backref='comment', cascade='all, delete-orphan')


class ReplyComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(1000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class CommentLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
