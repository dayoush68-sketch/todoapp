from flask import Flask, render_template, request, redirect, session
from AppDB import db, User, ToDo
import os


app = Flask(__name__,  template_folder="templates")
app.secret_key = "zxcvqwed0412"
app.config['TEMPLATES_AUTO_RELOAD'] = True
print("TEMPLATE FOLDER:", os.path.abspath(app.template_folder))

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

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
    todos  = ToDo.query.all()
    return render_template("index.html", todos = todos)

@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    deadline = request.form.get("deadline")


    new_todo = ToDo(title=title, deadline = deadline)
    db.session.add(new_todo)
    db.session.commit()
    return redirect("/")

@app.route("/delete/<int:index>")
def delete(index):
    if 0 <= index < len(ToDo):
        ToDo.pop(index)
    return redirect("/")


@app.route("/edit/<int:index>")
def edit(index):
    print("EDIT FUNCTION CALLED, index =", index)
    print("TODO DATA =", ToDo[index])
    print("TYPE =", type(ToDo[index]))
    if 0 <= index < len(ToDo):
        print("Rendering edit.html")
        return render_template("edit.html", index=index, todo=ToDo[index])
    print("Redirecting to /")
    return redirect("/")

@app.route("/update/<int:index>", methods=["POST"])
def update(index):
    if 0 <= index < len(ToDo):
        ToDo[index]["title"] = request.form.get("title")
        ToDo[index]["deadline"] = request.form.get("deadline")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)


