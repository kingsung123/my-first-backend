from flask import Flask, request, make_response
import json
import sqlite3

app = Flask(__name__)
DATABASE = 'todo.db'

def _json_response(data, status=200):
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.status_code = status
    return response

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            is_done INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 預設新增一個使用者
    cursor.execute("SELECT * FROM users WHERE username = 'testuser'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('testuser', '1234'))

    conn.commit()
    conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return _json_response({'message': '登入成功', 'user_id': user['id']})
    else:
        return _json_response({'message': '登入失敗'}, status=401)

@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.get_json()
    user_id = data.get('user_id')
    title = data.get('title')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO todos (user_id, title) VALUES (?, ?)", (user_id, title))
    conn.commit()
    conn.close()

    return _json_response({'message': '任務新增成功'})

@app.route('/todos/<int:user_id>', methods=['GET'])
def get_todos(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, is_done FROM todos WHERE user_id = ?", (user_id,))
    todos = [{'id': row[0], 'title': row[1], 'is_done': row[2]} for row in cursor.fetchall()]
    conn.close()
    return _json_response(todos)

@app.route('/todos', methods=['GET'])
def get_all_todos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, is_done, user_id FROM todos")
    todos = [{'id': row[0], 'title': row[1], 'is_done': row[2], 'user_id': row[3]} for row in cursor.fetchall()]
    conn.close()
    return _json_response(todos)

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    is_done = data.get('is_done', 0)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE todos SET is_done = ? WHERE id = ?", (is_done, todo_id))
    conn.commit()
    conn.close()
    return _json_response({'message': '任務已更新'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
