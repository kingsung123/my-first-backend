from flask import Flask, request, make_response
import sqlite3
import json

app = Flask(__name__)
DATABASE = 'todo_app.db'

# ---------------------------
# 資料庫初始化與連線函式
# ---------------------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def _json_response(data, status=200):
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.status_code = status
    return response

# ---------------------------
# 使用者登入
# ---------------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                        (username, password)).fetchone()
    conn.close()

    if user:
        return _json_response({'message': '登入成功', 'user_id': user['id']})
    else:
        return _json_response({'message': '帳號或密碼錯誤'}, 401)

# ---------------------------
# 建立任務
# ---------------------------
@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    title = data.get('title')
    user_id = data.get('user_id')
    
    conn = get_db_connection()
    conn.execute('INSERT INTO todos (title, user_id, is_done) VALUES (?, ?, ?)',
                 (title, user_id, 0))
    conn.commit()
    conn.close()
    return _json_response({'message': '任務已建立'})

# ---------------------------
# 更新任務狀態
# ---------------------------
@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    is_done = data.get('is_done', False)
    
    conn = get_db_connection()
    conn.execute('UPDATE todos SET is_done = ? WHERE id = ?', (int(is_done), todo_id))
    conn.commit()
    conn.close()
    
    return _json_response({'message': '任務狀態已更新'})

# ---------------------------
# 查詢使用者任務
# ---------------------------
@app.route('/todos/<int:user_id>', methods=['GET'])
def list_todos(user_id):
    conn = get_db_connection()
    todos = conn.execute('SELECT * FROM todos WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()

    return _json_response({'todos': [dict(todo) for todo in todos]})

# ---------------------------
# 初始化資料庫（第一次用）
# ---------------------------
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            is_done INTEGER NOT NULL DEFAULT 0,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    # 預設一個使用者
    conn.execute('INSERT OR IGNORE INTO users (id, username, password) VALUES (?, ?, ?)', 
                 (1, 'testuser', '1234'))
    conn.commit()
    conn.close()

# ---------------------------
# 主程式啟動
# ---------------------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
