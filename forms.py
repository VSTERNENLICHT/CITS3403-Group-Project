from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField, SelectField, IntegerField, FieldList, FormField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, NumberRange
from models import db, User
import sqlalchemy as sa

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class Sign_upForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email(message='Invalid email address.')])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, message="Must be 8+ characters long.")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError('Email already registered.')

class AssessmentForm(FlaskForm):
    class Meta:
        csrf = False
    atype = StringField('Assessment Type')
    weight = IntegerField('Weight (%)')
    max_mark = IntegerField('Available Marks')
    student_mark = IntegerField('Your Marks')

class UnitForm(FlaskForm):
    class Meta:
        csrf = False
    unit = StringField('Unit Code')
    semester = StringField('Semester')
    year = StringField('Year')
    assessments = FieldList(FormField(AssessmentForm), min_entries=1)

class PreviousUnitForm(FlaskForm):
    class Meta:
        csrf = False
    unit = StringField('Unit Code')
    semester = StringField('Semester')
    year = StringField('Year')
    mark = IntegerField('Your Mark (%)')

class PreviousUnitTabForm(FlaskForm):
    class Meta:
        csrf = False
    previous_units = FieldList(FormField(PreviousUnitForm), min_entries=1)

class CalcForm(FlaskForm):
    previous_units_tab = FieldList(FormField(PreviousUnitTabForm), min_entries=1, max_entries=1)
    units = FieldList(FormField(UnitForm))
