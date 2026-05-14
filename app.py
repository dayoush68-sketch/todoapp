from flask import Flask, render_template, request, redirect, session
from AppDB import db
import os


app = Flask(__name__,  template_folder="templates")
app.secret_key = "zxcvqwed0412"
app.config['TEMPLATES_AUTO_RELOAD'] = True
print("TEMPLATE FOLDER:", os.path.abspath(app.template_folder))
print("DB PATH:", os.path.abspath("todo.db"))

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

from AppDB import User, ToDo

# タスクは辞書形式で保存
# { "title": "買い物", "deadline": "2024-05-01" }
#todos = []
# ログインは辞書形式で保存
# { "id": "ログイン", "パスワード": "password" }
#logins = []


@app.route("/users", methods=["GET", "POST"])
def users():
    if request.method == "POST":
        print("=== POST DATA ===")
        print("request.form:", request.form)
        print("username:", request.form.get("username"))
        print("password:", request.form.get("password"))
        print("=================")             
        username = request.form.get("username")
        password = request.form.get("password")

        # 新規ユーザ作成
        user = User(username=username)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return redirect("/users")

    # GET のときは一覧表示
    users = User.query.all()
    return render_template("users.html", users=users)

@app.route("/users/<username>")
def user_page(username):
    #ログインしていない場合はログイン画面に戻る。
    if "user" not in session:
        return redirect("/login")
    
    #現在のユーザを定義
    current_user = User.query.filter_by(username=session["user"]).first()

    #管理者以外は自分のページしか見れない
    if current_user.username != username and not current_user.is_admin:
        return "権限がありません", 403
    
    #表示対象のユーザを定義
    target_user = User.query.filter_by(username=username).first()
    if target_user is None:
        return "ユーザが存在しません", 404
    
    #そのユーザのタスク一覧
    user_todos = ToDo.query.filter_by(user_id = target_user.id).all()
    return render_template("user_page.html",user=target_user, user_todos = user_todos)



@app.route("/users/delete/<int:id>")
def delete_user(id):
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect("/users")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def loginadd():
    print("★★★ loginadd() が呼ばれた ★★★")
    print("LOGIN POST:", request.form)
    id =  request.form.get("username")
    password = request.form.get("password")

    user = User.query.filter_by(username=id).first()

    if user and user.check_password(password):
        session["user"] = id

        return redirect("/")
    else:
        return render_template("login.html", error="IDまたはパスワードが違います") 

@app.route("/logout")
def logout():
    session.pop("user", None)  # Flask側のログイン情報を削除
    return redirect("/login")
    

@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    current_user = User.query.filter_by(username=session["user"]).first()
    todos = ToDo.query.filter_by(user_id=current_user .id).all()
    return render_template("index.html", todos = todos, username = current_user.username)

@app.route("/add", methods=["POST"])
def add():
    if "user" not in session:
        return redirect("/login")
    title = request.form.get("title")
    deadline = request.form.get("deadline")

    users = User.query.filter_by(username=session["user"]).first()
    new_todo = ToDo(title=title, deadline = deadline, user_id=users.id)
    db.session.add(new_todo)
    db.session.commit()
    return redirect("/")

@app.route("/delete/<int:todo_id>")
def delete(todo_id):
  if "user" not in session:
        return redirect("/login")
  print("削除しようとしているID:", todo_id)
  todo = ToDo.query.get(todo_id)
  print("取得したtodo:", todo)
  if todo is None:
      return redirect("/") 
  db.session.delete(todo)
  db.session.commit()
  return redirect("/")


@app.route("/edit/<int:edit_id>", methods=["GET"])
def edit(edit_id):
   if "user" not in session:
        return redirect("/login")
   print("編集しようとしているToDo:", edit_id)
   todo = ToDo.query.get(edit_id)
   print("編集したToDo:", edit_id)
   if todo is None:
        return redirect("/")
   
   return render_template("edit.html", todo = todo)

@app.route("/update/<int:edit_id>", methods=["POST"])
def update(edit_id):
   if "user" not in session:
        return redirect("/login")
   todo = ToDo.query.get(edit_id)
   if todo is None:
        return redirect("/")
   
   todo.title = request.form.get("title")
   todo.deadline = request.form.get("deadline")

   db.session.commit()
   return redirect("/")

if __name__ == "__main__":
    with app.app_context():
     db.create_all()
    app.run(debug=True)


