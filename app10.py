from flask import Flask, request, make_response
import sqlite3
import json

app = Flask(__name__)

# 建立資料庫連線
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# 初始化資料庫（只執行一次）
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
            user_id INTEGER,
            task TEXT NOT NULL,
            is_done BOOLEAN DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

# 統一的 JSON 回傳（含 UTF-8 編碼）
def _json_response(data, status=200):
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.status_code = status
    return response

# 註冊帳號
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return _json_response({'message': '註冊成功'})
    except sqlite3.IntegrityError:
        return _json_response({'message': '用戶已存在'}, status=409)
    finally:
        conn.close()

# 登入
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
    conn.close()
    if user:
        return _json_response({'message': '登入成功', 'user_id': user['id']})
    else:
        return _json_response({'message': '登入失敗'}, status=401)

# 新增任務
@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.get_json()
    user_id = data.get('user_id')
    task = data.get('task')
    conn = get_db_connection()
    conn.execute('INSERT INTO todos (user_id, task) VALUES (?, ?)', (user_id, task))
    conn.commit()
    conn.close()
    return _json_response({'message': '任務新增成功'})

# 取得任務清單
@app.route('/todos', methods=['GET'])
def get_todos():
    user_id = request.args.get('user_id')
    conn = get_db_connection()
    todos = conn.execute('SELECT id, task, is_done FROM todos WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    return _json_response([dict(todo) for todo in todos])

# 主程式
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
