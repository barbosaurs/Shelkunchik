from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

class RegisterForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    password_confirm = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password', message='Пароли должны совпадать')])
    submit = SubmitField('Зарегистрироваться')
