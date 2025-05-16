from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class TaskForm(FlaskForm):
    title = StringField('Название задачи', validators=[DataRequired(), Length(min=5, max=200)])
    description = TextAreaField('Условие задачи', validators=[DataRequired()])
    correct_answer = StringField('Правильный ответ', validators=[DataRequired()])
    solution = TextAreaField('Решение задачи', validators=[DataRequired()])
    category_id = SelectField('Категория', coerce=int, validators=[DataRequired()])
    image = FileField('Загрузить изображение', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Только изображения!'),
        FileRequired('Файл обязателен для загрузки')
    ])

    submit = SubmitField('Добавить задачу')
