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
    
    # 預設使用者和一些中文測試資料
    c.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'testuser', '1234')")
    c.execute("INSERT OR IGNORE INTO todos (id, user_id, title, is_done) VALUES (1, 1, '買牛奶', 0)")
    c.execute("INSERT OR IGNORE INTO todos (id, user_id, title, is_done) VALUES (2, 1, '餵牛', 1)")
    c.execute("INSERT OR IGNORE INTO todos (id, user_id, title, is_done) VALUES (3, 1, '寫程式', 0)")
    c.execute("INSERT OR IGNORE INTO todos (id, user_id, title, is_done) VALUES (4, 1, '學習 Python', 0)")
    conn.commit()
    conn.close()

# 自訂 JSON 回應格式
def _json_response(data, status=200):
    response = make_response(json.dumps(data, ensure_ascii=False, indent=2))
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

# 搜尋待辦事項（改進版，更好的中文支援）
@app.route('/todos/search', methods=['GET'])
def search_todos():
    keyword = request.args.get('keyword', '')
    
    # 輸出原始接收到的 keyword 以便除錯
    print(f"原始 keyword: {repr(keyword)}")
    
    if not keyword:
        return _json_response({'message': '請提供搜尋關鍵字'}, 400)
    
    # 嘗試多種解碼方式來處理中文
    decoded_keyword = keyword
    try:
        # 方法1: 直接 URL 解碼
        decoded_keyword = unquote(keyword, encoding='utf-8')
        print(f"URL 解碼後: {repr(decoded_keyword)}")
    except Exception as e:
        print(f"URL 解碼失敗: {e}")
        try:
            # 方法2: 嘗試從 latin-1 轉 utf-8 (處理 Windows CMD 編碼問題)
            decoded_keyword = keyword.encode('latin-1').decode('utf-8')
            print(f"Latin-1 to UTF-8 轉換後: {repr(decoded_keyword)}")
        except Exception as e2:
            print(f"Latin-1 轉換也失敗: {e2}")
            # 方法3: 嘗試從 cp950 (繁體中文) 解碼
            try:
                decoded_keyword = keyword.encode('latin-1').decode('cp950')
                print(f"CP950 解碼後: {repr(decoded_keyword)}")
            except Exception as e3:
                print(f"CP950 解碼也失敗: {e3}")
                decoded_keyword = keyword
    
    if not decoded_keyword:
        return _json_response({'message': '搜尋關鍵字無效'}, 400)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, title, is_done FROM todos")
    all_todos = cursor.fetchall()
    conn.close()

    matched_todos = []
    keyword_lower = decoded_keyword.lower()
    
    print(f"最終搜尋關鍵字: {repr(keyword_lower)}")

    for row in all_todos:
        title = str(row['title'])
        print(f"比對標題: {repr(title)}")
        if keyword_lower in title.lower():
            matched_todos.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'title': title,
                'is_done': row['is_done']
            })

    return _json_response({
        'message': f'找到 {len(matched_todos)} 個匹配的任務' if matched_todos else '沒有找到匹配的任務',
        'keyword': decoded_keyword,
        'original_keyword': keyword,  # 顯示原始接收到的關鍵字
        'todos': matched_todos
    })

# 新增 POST 方式的搜尋，避免 URL 編碼問題
@app.route('/todos/search', methods=['POST'])
def search_todos_post():
    data = request.get_json()
    if not data:
        return _json_response({'message': '請提供 JSON 資料'}, 400)
    
    keyword = data.get('keyword', '')
    print(f"POST 搜尋關鍵字: {repr(keyword)}")
    
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

    return _json_response({
        'message': f'找到 {len(matched_todos)} 個匹配的任務' if matched_todos else '沒有找到匹配的任務',
        'keyword': keyword,
        'todos': matched_todos
    })

# 新增一個測試路由來檢查中文處理
@app.route('/test/chinese', methods=['GET'])
def test_chinese():
    return _json_response({
        'message': '中文測試成功',
        'sample_data': ['買牛奶', '餵牛', '學習Python']
    })

# 初始化資料庫
init_db()

# 啟動伺服器
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)