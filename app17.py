from flask import Flask, request, jsonify, make_response
import sqlite3
import json

app = Flask(__name__)
DATABASE = 'todos.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def _json_response(data, status=200):
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.status_code = status
    return response

# 建立資料表（初次執行可用）
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
            title TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

# 建立使用者
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return _json_response({'message': f'使用者 {username} 建立成功'})
    except sqlite3.IntegrityError:
        return _json_response({'error': '使用者已存在'}, 400)
    finally:
        conn.close()

# 建立代辦事項
@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    title = data.get('title')
    user_id = data.get('user_id')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO todos (title, user_id) VALUES (?, ?)', (title, user_id))
    conn.commit()
    conn.close()

    return _json_response({'message': '代辦事項新增成功'})

# 取得所有代辦事項
@app.route('/todos', methods=['GET'])
def get_todos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM todos')
    todos = cursor.fetchall()
    conn.close()

    result = [{'id': row['id'], 'title': row['title'], 'user_id': row['user_id']} for row in todos]
    return _json_response(result)

# 刪除代辦事項
@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()

    return _json_response({'message': f'代辦事項 {todo_id} 已刪除'})

# 啟動前初始化資料庫
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
