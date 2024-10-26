from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, IntegerField, BooleanField, SelectMultipleField, widgets, SubmitField
from wtforms.validators import DataRequired, Email, Length
from wtforms.fields import DateField, TimeField
from wtforms_components import DateRange
from datetime import datetime, date, timedelta
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.widgets import html_params


# geo_url = api.geonames.org/citiesJSON?


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])

    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=6)])
    ethnicity = SelectField('Ethnicity', choices=[
        ('', 'Select your ethnicity'),  # Placeholder option
        ('asian', 'Asian'), ('black', 'Black'), (
            'hispanic', 'Hispanic'), ('white', 'White')], validators=[DataRequired()])
    profession = SelectField('Profession', choices=[
        ('', 'Select a profession'),  # Placeholder option
        ('administrative', 'Administrative/Office Support'),
        ('education', 'Education/Teaching'),
        ('healthcare', 'Healthcare/Medical'),
        ('information_technology', 'Information Technology'),
        ('management', 'Management/Executive'),
        ('sales', 'Sales/Customer Service'),
        ('finance', 'Finance/Accounting'),
        ('engineering', 'Engineering'),
        ('arts', 'Arts/Entertainment'),
        ('business', 'Business/Entrepreneurship'),
        ('consulting', 'Consulting'),
        ('customer_service', 'Customer Service'),
        ('design', 'Design/Creative'),
        ('hospitality', 'Hospitality/Tourism'),
        ('human_resources', 'Human Resources'),
        ('legal', 'Legal'),
        ('marketing', 'Marketing/Advertising'),
        ('nonprofit', 'Nonprofit/Volunteering'),
        ('research', 'Research/Analysis'),
        ('retail', 'Retail/Wholesale'),
        ('social_services', 'Social Services'),
        ('writing_editing', 'Writing/Editing'),
        ('grade_school_student', 'K-12 Student'),
        ('post_secondary_student', 'Post Secondary Education Student'),
        ('other', 'Other')
    ], validators=[DataRequired()])

    financial_status_range = SelectField('Financial Status Range', choices=[
        ('', 'Select your household income range'),  # Placeholder option
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], validators=[DataRequired()])

    education_level = SelectField('Education Level', choices=[
        ('', 'Select your education level'),  # Placeholder option
        ('high_school_diploma', 'High School Diploma'),
        ('associates_degree', "Associate's Degree"),
        ('bachelors_degree', "Bachelor's Degree"),
        ('masters_degree', "Master's Degree"),
        ('doctorate', 'Doctorate'),
        ('certificate', 'Certificate'),
        ('vocational_training', 'Vocational Training'),
        ('technical_degree', 'Technical Degree'),
        ('professional_degree', 'Professional Degree'),
        ('postgraduate_diploma', 'Postgraduate Diploma'),
        ('other', 'Other')

    ], validators=[DataRequired()])

    location_general = StringField('Location', validators=[
                                   DataRequired()], render_kw={"placeholder": "Search your area by postal code"})  # Postal code field


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class JournalForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    text_entry = TextAreaField('Text Entry', validators=[DataRequired()])


class MultiCheckboxField(SelectMultipleField):
    # widget = widgets.ListWidget(prefix_label=False, )
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class GoalForm(FlaskForm):
    goal_text = StringField('Goal Text', validators=[
                            DataRequired(), Length(max=150)])
    days_of_week = MultiCheckboxField('What days would you work you work on your goal?', choices=[
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ], render_kw={'class': 'checkbox-list'})
    reminder_time = TimeField(
        'When would you like to be reminded?', validators=[DataRequired()])
    # frequency = IntegerField('How many times do ', validators=[DataRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d', default=datetime.today(),
                           validators=[DateRange(min=date.today())],
                           render_kw={
        'min': date.today().strftime('%Y-%m-%d'),
        'max': (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
    })
    # end_date = StringField('Your End Date is:', render_kw={'readonly': True})
  
    # Calculate default end_date based on start_date + 14 days
    default_end_date = date.today() + timedelta(days=14)
    end_date = DateField('Your End Date Is:', validators=[
                         DataRequired()], format='%Y-%m-%d', default=default_end_date, render_kw={'readonly': True})
    # completed = BooleanField('Completed')

class GoalDaysForm(FlaskForm):
    # Assuming you'll dynamically add BooleanFields for each goal day in the view function
    complete_goal = SubmitField('Complete Goal')