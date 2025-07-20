from flask import Flask, request, make_response
import sqlite3
import json

app = Flask(__name__)
DB_NAME = 'todo.db'

# ---------- 共用 JSON 回應格式 ----------
def _json_response(data, status=200):
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.status_code = status
    return response

# ---------- 初始化資料庫 ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            is_done INTEGER DEFAULT 0,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

# ---------- 建立使用者 ----------
@app.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return _json_response({'error': '請提供使用者名稱與密碼'}, 400)

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()
    return _json_response({'message': '使用者建立成功'}, 201)

# ---------- 建立代辦事項 ----------
@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    title = data.get('title')
    user_id = data.get('user_id')

    if not title or not user_id:
        return _json_response({'error': '請提供代辦事項標題與使用者 ID'}, 400)

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO todos (title, user_id) VALUES (?, ?)', (title, user_id))
    conn.commit()
    conn.close()
    return _json_response({'message': '代辦事項建立成功'}, 201)

# ---------- 取得單一使用者的代辦事項 ----------
@app.route('/todos/<int:user_id>', methods=['GET'])
def get_todos(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, title, is_done FROM todos WHERE user_id = ?', (user_id,))
    todos = [{'id': row[0], 'title': row[1], 'is_done': row[2]} for row in c.fetchall()]
    conn.close()
    return _json_response(todos)

# ---------- 主程式入口 ----------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
