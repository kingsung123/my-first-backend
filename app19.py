from flask import Flask, request, jsonify, make_response
import sqlite3
import json
from urllib.parse import unquote

app = Flask(__name__)

# 連接資料庫
def get_db_connection():
    conn = sqlite3.connect('todos.db')
    conn.row_factory = sqlite3.Row
    return conn

# 初始化資料庫
def init_db():
    conn = get_db_connection()
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
    
    # 預設使用者
    c.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'testuser', '1234')")
    conn.commit()
    conn.close()

# 自訂 JSON 回應格式
def _json_response(data, status=200):
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.status_code = status
    return response

# 登入
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username=? AND password=?', (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        return _json_response({'message': '登入成功', 'user_id': user[0]})
    else:
        return _json_response({'message': '帳號或密碼錯誤'}, 401)

# 新增待辦事項
@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.get_json()
    user_id = data.get('user_id')
    title = data.get('title')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO todos (user_id, title) VALUES (?, ?)', (user_id, title))
    conn.commit()
    conn.close()
    return _json_response({'message': '任務新增成功'})

# 查詢指定使用者的待辦事項
@app.route('/todos/<int:user_id>', methods=['GET'])
def get_user_todos(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, title, is_done FROM todos WHERE user_id=?', (user_id,))
    todos = [{'id': row[0], 'title': row[1], 'is_done': row[2]} for row in c.fetchall()]
    conn.close()
    return _json_response(todos)

# 查詢所有待辦事項
@app.route('/todos', methods=['GET'])
def get_all_todos():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, user_id, title, is_done FROM todos')
    todos = [{'id': row[0], 'user_id': row[1], 'title': row[2], 'is_done': row[3]} for row in c.fetchall()]
    conn.close()
    return _json_response(todos)

# 更新待辦事項
@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    title = data.get('title')
    is_done = data.get('is_done')

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE todos SET title = ?, is_done = ? WHERE id = ?', (title, is_done, todo_id))
    conn.commit()
    conn.close()
    return _json_response({'message': '任務更新成功'})

# 刪除待辦事項
@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()
    return _json_response({'message': '任務刪除成功'})

# 搜尋待辦事項（支援中文）
@app.route('/todos/search', methods=['GET'])
def search_todos():
    keyword = request.args.get('keyword', '')

    # 解碼 URL 字串，確保中文字正確顯示
    keyword = unquote(keyword)

    if not keyword:
        return _json_response({'message': '請提供搜尋關鍵字'}, 400)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, title, is_done FROM todos")
    all_todos = cursor.fetchall()
    conn.close()

    matched_todos = []
    keyword_lower = keyword.lower()

    for row in all_todos:
        title = str(row['title'])
        if keyword_lower in title.lower():
            matched_todos.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'title': title,
                'is_done': row['is_done']
            })

    if matched_todos:
        return _json_response({
            'message': f'找到 {len(matched_todos)} 個匹配的任務',
            'keyword': keyword,
            'todos': matched_todos
        })
    else:
        return _json_response({
            'message': '沒有找到匹配的任務',
            'keyword': keyword,
            'todos': []
        })

# 初始化資料庫
init_db()

# 啟動伺服器
if __name__ == '__main__':
    app.run(debug=True)
