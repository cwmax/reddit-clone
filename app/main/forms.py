from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired


class CreateSiteForm(FlaskForm):
    site_name = StringField('Site Name', validators=[DataRequired()])
    submit = SubmitField('Create new site')


class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit post')


class CommentForm(FlaskForm):
    parent_comment_id = HiddenField("Parent comment id")
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit post')
