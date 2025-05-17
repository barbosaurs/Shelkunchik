import os
import argparse
from argparse import ArgumentParser
import datetime as dt

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_wtf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import alias
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from data import db_session
from data.__all_models import User, Category, Task, UserTask
from forms.answer import AnswerForm
from forms.category_add import CategoryForm
from forms.register import RegisterForm
from forms.login import LoginForm
from forms.task_add import TaskForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'

# Инициализация CSRF
csrf = CSRFProtect(app)

app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = None

# Инициализация LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

os.makedirs("db", exist_ok=True)
db_session.global_init("db/database.db")

session = db_session.create_session()
user = session.query(User).filter(User.username == "admin").first()
if not user:
    user = User(
        username="admin",
        password=generate_password_hash("admin_password")
    )
    session.add(user)
    session.commit()
session.close()


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(int(user_id))
    session.close()
    return user


@app.route('/')
def index():
    session = db_session.create_session()

    categories = session.query(Category).all()
    category_id = request.args.get('category_id', type=int)
    query = session.query(Task)
    if category_id:
        query = query.filter(Task.category_id == category_id)
    tasks = query.all()

    if current_user.is_authenticated:
        user_tasks = session.query(UserTask).filter(UserTask.user_id == current_user.id).all()
        incorrect_tasks = {t.task_id for t in user_tasks if not t.is_correct}
        correct_tasks = {t.task_id for t in user_tasks if t.is_correct}
        for task in tasks:
            category = session.query(Category).get(task.category_id)
            if category:
                task.category_name = category.name
            else:
                task.category_name = ""
            task.is_incorrect = task.id in incorrect_tasks
            task.is_correct = task.id in correct_tasks
    session.close()
    return render_template('index.html', tasks=tasks, categories=categories, selected_category=category_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        if session.query(User).filter(User.username == form.username.data).first():
            flash("Пользователь с таким логином уже существует", "danger")
            session.close()
            return render_template('auth/register.html', form=form)
        user = User(
            username=form.username.data,
            password=generate_password_hash(form.password.data)
        )
        session.add(user)
        session.commit()
        session.close()
        flash("Вы успешно зарегистрировались!", "success")
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.username == form.username.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Вы успешно вошли в систему!", "success")
            return redirect(url_for('index'))

        # Если пользователь не найден или пароль неверный
        flash("Неправильный логин или пароль", "danger")
        return render_template('auth/login.html', form=form)  # Остаемся на странице входа

    return render_template('auth/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('index'))


@app.route('/task/<int:task_id>', methods=['GET', 'POST'])
def view_task(task_id):
    form = AnswerForm()
    session = db_session.create_session()
    task = session.query(Task).get(task_id)
    if not task:
        abort(404)
    if form.validate_on_submit():
        answer = form.answer.data
        if current_user.is_authenticated:
            user_task = session.query(UserTask).filter(UserTask.user_id == current_user.get_id(),
                                                       UserTask.task_id == task_id).first()
            if user_task:
                if answer == task.correct_answer:
                    flash('Ответ правильный, но вы уже решали эту задачу', 'success')
                else:
                    flash(f'Ответ неверный! Решение: {task.solution}', 'danger')
            else:
                if answer.lower() == task.correct_answer.lower():
                    flash('Ответ правильный!', 'success')
                    user = session.query(User).get(current_user.get_id())
                    setattr(user, 'solved_tasks', user.solved_tasks + 1)
                    session.commit()
                    user_task_add = UserTask(
                        user_id=current_user.get_id(),
                        task_id=task_id,
                        is_correct=True
                    )
                    session.add(user_task_add)
                else:
                    flash(f'Ответ неверный! Решение: {task.solution}', 'danger')
                    user_task_add = UserTask(
                        user_id=current_user.get_id(),
                        task_id=task_id,
                        is_correct=False
                    )
                    session.add(user_task_add)
                session.commit()
                session.close()
        else:
            flash("Авторизуйтесь, чтобы узнать правильный ответ")
        return redirect(url_for('view_task', task_id=task_id))

    return render_template('task.html', task=task, form=form)


@app.route('/account')
@login_required
def account():
    session = db_session.create_session()
    user_tasks = session.query(UserTask).filter(UserTask.user_id == current_user.id).all()
    total_tasks = len(user_tasks)
    solved_tasks = sum(1 for t in user_tasks if t.is_correct)
    session.close()

    return render_template('account.html', total_tasks=total_tasks, solved_tasks=solved_tasks)


@app.route('/leaderboard')
def leaderboard():
    db_sess = db_session.create_session()
    users = db_sess.query(User).order_by(User.solved_tasks.desc()).all()
    return render_template('leaderboard.html', users=users)


@app.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    if current_user.username != "admin":
        return "Нет доступа"
    form = CategoryForm()
    session = db_session.create_session()

    if form.validate_on_submit():
        new_category = Category(name=form.name.data)
        session.add(new_category)
        session.commit()
        flash('Категория добавлена!', 'success')
        return redirect(url_for('manage_categories'))

    categories = session.query(Category).all()
    session.close()
    return render_template('manage_categories.html', categories=categories, form=form)


@app.route('/categories/delete/<int:category_id>', methods=['GET'])
@login_required
def delete_category(category_id):
    if current_user.username != "admin":
        return "Нет доступа"
    session = db_session.create_session()
    category = session.query(Category).get(category_id)
    if category:
        session.delete(category)
        session.commit()
        flash('Категория удалена!', 'success')
    session.close()
    return redirect(url_for('manage_categories'))


@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def manage_tasks():
    if current_user.username != "admin":
        return "Нет доступа"
    form = TaskForm()
    session = db_session.create_session()
    form.category_id.choices = [(c.id, c.name) for c in session.query(Category).all()]

    image_folder = "static/images/tasks"
    os.makedirs(image_folder, exist_ok=True)

    if form.validate_on_submit():
        image = form.image.data
        has_image = False
        now = dt.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        if image:
            has_image = True
            extension = secure_filename(image.filename).split(".")[-1]
            image_name = f"{now}.{extension}"
            image.save(os.path.join(f"static/images/tasks", image_name))
        task = Task(
            title=form.title.data,
            description=form.description.data,
            correct_answer=form.correct_answer.data,
            solution=form.solution.data,
            category_id=form.category_id.data,
            has_image=has_image,
            image_name=image_name if has_image else None
        )
        session.add(task)
        session.commit()
        flash('Задача добавлена!', 'success')
        return redirect(url_for('manage_tasks'))

    tasks = session.query(Task).all()
    session.close()

    return render_template('manage_tasks.html', form=form, tasks=tasks)


@app.route('/tasks/delete/<int:task_id>', methods=['GET'])
@login_required
def delete_task(task_id):
    if current_user.username != "admin":
        return "Нет доступа"
    session = db_session.create_session()
    task = session.query(Task).get(task_id)
    user_tasks = session.query(UserTask).filter(UserTask.task_id == task.id).all()
    for user_task in user_tasks:
        session.delete(user_task)
        session.commit()
    if task:
        session.delete(task)
        session.commit()
        flash('Задача удалена!', 'success')
    session.close()
    return redirect(url_for('manage_tasks'))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--port', type=int, default=5000)

    args = parser.parse_args()
    app.run(host='0.0.0.0', port=args.port, debug=False)
