from flask import Flask, request, make_response
import sqlite3
import json

app = Flask(__name__)

# ======= 資料庫初始化 =======
def init_db():
    conn = sqlite3.connect('todo.db')
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
            is_done INTEGER NOT NULL DEFAULT 0,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ======= 自定義 JSON 回應（UTF-8）=======
def _json_response(data, status=200):
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.status_code = status
    return response

# ======= 建立使用者 =======
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return _json_response({'error': '缺少使用者名稱或密碼'}, 400)

    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    user_id = c.lastrowid
    conn.close()

    return _json_response({'message': '使用者建立成功', 'user_id': user_id}, 201)

# ======= 建立待辦事項 =======
@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    title = data.get('title')
    user_id = data.get('user_id')

    if not title or not user_id:
        return _json_response({'error': '缺少標題或使用者 ID'}, 400)

    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("INSERT INTO todos (title, user_id) VALUES (?, ?)", (title, user_id))
    conn.commit()
    todo_id = c.lastrowid
    conn.close()

    return _json_response({'message': '代辦事項建立成功', 'todo_id': todo_id}, 201)

# ======= 取得某個使用者的代辦清單 =======
@app.route('/todos/<int:user_id>', methods=['GET'])
def get_todos(user_id):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT id, title, is_done FROM todos WHERE user_id = ?", (user_id,))
    todos = [{'id': row[0], 'title': row[1], 'is_done': row[2]} for row in c.fetchall()]
    conn.close()

    return _json_response(todos)

# ======= 執行應用程式 =======
if __name__ == '__main__':
    app.run(debug=True)
