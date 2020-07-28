from flask_wtf import FlaskForm
from wtforms import Form, StringField, SubmitField, SelectField, IntegerField, FormField, FieldList
from wtforms.validators import DataRequired, NumberRange

class StatisticalTestForm(FlaskForm):
    # We will append choices to drop down depending on the data and what is selected by the upser
    # as survey takes an objectId as the value, we need to initialise it and also tell it to coerce ObjectIds
    test = SelectField(choices=[("", " -- select an option -- "), ("Kruskall Wallis Test", "Kruskall Wallis Test"), ("Mann-Whitney U Test", "Mann-Whitney U Test"), ("Chi-Square Test", "Chi-Square Test"), ("Chi-Square goodness of fit", "Chi-Square goodness of fit")], validators=[DataRequired()])
    independent_variable = SelectField(choices=[("", " -- select an option -- ")], validators=[DataRequired()])
    # Having a second variable is optional in some tests (that only require a single variable) therefore have not included DataRequired()
    dependent_variable = SelectField(choices=[("", " -- select an option -- ")])
    submit = SubmitField("Continue")


class ChiGoodnessEntryForm(Form):
    key = StringField()
    expected = IntegerField(validators=[NumberRange(min=0, max=100)])


class ChiGoodnessForm(FlaskForm):
    field = FieldList(FormField(ChiGoodnessEntryForm))
    submit = SubmitField("Continue")

class SaveTestForm(FlaskForm):
    submit = SubmitField("Save to dashboard")
