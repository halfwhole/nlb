from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired

class AddForm(FlaskForm):
    brn = IntegerField('BRN', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    classification = StringField('Classification', validators=[DataRequired()])
    submit = SubmitField('Submit')

class DeleteForm(FlaskForm):
    number = IntegerField('Row number', validators=[DataRequired()])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    identifier = StringField('Identifier', validators=[DataRequired()])
    submit = SubmitField('Submit')
