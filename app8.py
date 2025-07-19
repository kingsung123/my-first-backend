from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo_auth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 使用者模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    todos = db.relationship('Todo', backref='user', lazy=True)

# 代辦事項模型
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# 根目錄提示
@app.route('/', methods=['GET'])
def index():
    return "✅ Flask 代辦事項系統運行中"

# 使用者註冊
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': '帳號和密碼不可為空'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '使用者已存在'}), 400
    password_hash = generate_password_hash(password)
    new_user = User(username=username, password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': '註冊成功'})

# 使用者登入
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': '帳號和密碼不可為空'}), 400
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return jsonify({'message': '登入成功', 'user_id': user.id})
    else:
        return jsonify({'error': '帳號或密碼錯誤'}), 401

# 新增代辦事項
@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    task = data.get('task')
    user_id = data.get('user_id')
    if not task or not user_id:
        return jsonify({'error': '任務內容及使用者ID皆為必填'}), 400
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '找不到使用者'}), 404
    new_todo = Todo(task=task, user_id=user_id)
    db.session.add(new_todo)
    db.session.commit()
    return jsonify({'message': '代辦事項已新增', 'todo_id': new_todo.id})

# 查詢所有代辦事項
@app.route('/todos', methods=['GET'])
def get_all_todos():
    todos = Todo.query.all()
    return jsonify([
        {'id': todo.id, 'task': todo.task, 'user_id': todo.user_id}
        for todo in todos
    ])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
