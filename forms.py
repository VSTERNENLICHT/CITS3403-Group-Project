from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField, SelectField, IntegerField, FieldList, FormField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange
from models import db, User
import sqlalchemy as sa

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class Sign_upForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError('Email already registered. Please use a different email.')


class AssessmentForm(FlaskForm):
    class Meta:
        csrf = False
    atype = StringField('Assessment Type')
    weight = IntegerField('Weight (%)', validators=[NumberRange(min=0, max=100)])
    max_mark = IntegerField('Available Marks', validators=[NumberRange(min=0)])
    student_mark = IntegerField('Your Marks', validators=[NumberRange(min=0, max=100)])

class UnitForm(FlaskForm):
    class Meta:
        csrf = False
    unit = StringField('Unit Code', validators=[DataRequired()])
    semester = SelectField('Semester', choices=["Semester 1", "Semester 2"])
    year = SelectField('Year', choices=["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"])
    assessments = FieldList(FormField(AssessmentForm), min_entries=1)

class PreviousUnitForm(FlaskForm):
    class Meta:
        csrf = False
    unit = StringField('Unit Code', validators=[DataRequired()])
    semester = SelectField('Semester', choices=["Semester 1", "Semester 2"])
    year = SelectField('Year', choices=["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"])
    mark = IntegerField('Your Mark (%)', validators=[NumberRange(min=0, max=100)])

class PreviousUnitTabForm(FlaskForm):
    class Meta:
        csrf = False
    previous_units = FieldList(FormField(PreviousUnitForm), min_entries=1)

class CalcForm(FlaskForm):
    previous_units_tab = FieldList(FormField(PreviousUnitTabForm), min_entries=1, max_entries=1)
    units = FieldList(FormField(UnitForm), min_entries=1)
