from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')
