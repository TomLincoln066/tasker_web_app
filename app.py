from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '123'  # Add a secret key for session management


db = SQLAlchemy(app)
migrate = Migrate(app, db)

# define Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    status = db.Column(db.String(255))
    due_date = db.Column(db.String(255))
    user_name = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    tasks = db.relationship('Task', backref='user', lazy=True)


# create routes
@app.route('/', methods=["GET", "POST"])
def home():
    # if request.method == "POST":
    #     user_name = request.form.get("user_name")
    #     tasks = Task.query.filter_by(user_name=user_name).order_by(Task.due_date).all()
    #     return render_template("tasks.html", tasks=tasks)
    # return render_template("login.html")
    if request.method == "POST":
        user_name = request.form.get("user_name")
        user = User.query.filter_by(name=user_name).first()
        if user is None:
            user = User(name=user_name)
            db.session.add(user)
            db.session.commit()
        session['user_id'] = user.id
        return redirect(url_for('tasks'))
    return render_template("login.html")

@app.route('/create-task', methods=["GET", "POST"])
def create_task():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    if request.method == "POST":
        user_id = session['user_id']
        title = request.form.get("title")
        description = request.form.get("description")
        status = request.form.get("status")
        due_date = request.form.get("due_date")
        # user_name = request.form.get("user_name")
        # new_task = Task(title=title, description=description, status=status, due_date=due_date, user_name=user_name)
        new_task = Task(title=title, description=description, status=status, due_date=due_date, user_id=user_id)

        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('tasks'))
    return render_template("create_task.html")

@app.route('/delete-task/<id>', methods=["GET"])
def delete_task(id):
    task = Task.query.filter_by(id=id).first()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('tasks'))


@app.route('/tasks', methods=["GET"])
def tasks():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    user_id = session['user_id']
    user_name = User.query.get(user_id).name  # Get the user_name based on user_id

    # user = User.query.get(user_id)

    sort_by = request.args.get('sort_by')  # Get the sort_by query parameter

    # Define the sorting criteria based on the sort_by parameter
    if sort_by == 'title':
        tasks = Task.query.filter_by(user_id=user_id).order_by(Task.title).all()
    elif sort_by == 'status':
        tasks = Task.query.filter_by(user_id=user_id).order_by(Task.status).all()
    elif sort_by == 'due_date':
        tasks = Task.query.filter_by(user_id=user_id).order_by(Task.due_date).all()
    else:
        tasks = Task.query.filter_by(user_id=user_id).all()  # Default sorting

    # return render_template("tasks.html", user=user, tasks=tasks)
    return render_template("tasks.html", user_name=user_name, tasks=tasks)


#logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))


#edit tasks
@app.route('/edit-task/<id>', methods=["GET", "POST"])
def edit_task(id):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    task = Task.query.filter_by(id=id).first()
    if task is None:
        return redirect(url_for('tasks'))
    
    if request.method =="POST":
        task.title = request.form.get("title")
        task.description = request.form.get("description")
        task.status = request.form.get("status")
        task.due_date = request.form.get("due_date")
        db.session.commit()
        return redirect(url_for('tasks'))

    return render_template("edit_task.html", task=task)



#### 4. Running the App

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)