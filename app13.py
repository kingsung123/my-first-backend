from flask import Flask, request, make_response
import sqlite3
import json

app = Flask(__name__)

# 建立資料庫與資料表
def init_db():
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    # 使用者表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # 待辦事項表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            is_done INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    # 新增預設使用者
    c.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'testuser', '1234')")
    conn.commit()
    conn.close()

# 中文 JSON 回傳用的函式
def _json_response(data, status=200):
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.status_code = status
    return response

init_db()

# 登入
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username=? AND password=?', (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        return _json_response({'message': '登入成功', 'user_id': user[0]})
    else:
        return _json_response({'message': '帳號或密碼錯誤'}, status=401)

# 新增任務
@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.get_json()
    user_id = data.get('user_id')
    title = data.get('title')

    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('INSERT INTO todos (user_id, title) VALUES (?, ?)', (user_id, title))
    conn.commit()
    conn.close()
    return _json_response({'message': '任務新增成功'})

# 查詢指定使用者的任務
@app.route('/todos/<int:user_id>', methods=['GET'])
def get_user_todos(user_id):
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('SELECT id, title, is_done FROM todos WHERE user_id=?', (user_id,))
    todos = [{'id': row[0], 'title': row[1], 'is_done': row[2]} for row in c.fetchall()]
    conn.close()
    return _json_response(todos)

# 查詢所有任務
@app.route('/todos', methods=['GET'])
def get_all_todos():
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('SELECT id, user_id, title, is_done FROM todos')
    todos = [{'id': row[0], 'user_id': row[1], 'title': row[2], 'is_done': row[3]} for row in c.fetchall()]
    conn.close()
    return _json_response(todos)

# 更新任務完成狀態
@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    is_done = data.get('is_done')

    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('UPDATE todos SET is_done=? WHERE id=?', (is_done, todo_id))
    conn.commit()
    conn.close()
    return _json_response({'message': '任務更新成功'})

if __name__ == '__main__':
    app.run(debug=True)
