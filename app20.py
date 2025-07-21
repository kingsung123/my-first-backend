import sqlite3

# 設定資料庫連線
DATABASE = 'todos.db'

def search_todos(keyword):
    # 連接資料庫
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 搜尋待辦事項，並打印出相對應的 SQL 查詢語句
    query = "SELECT id, title, is_done FROM todos WHERE title LIKE ?"
    print(f"執行的查詢語句: {query}，關鍵字: {keyword}")
    
    cursor.execute(query, ('%' + keyword + '%',))  # 這裡使用 LIKE 來模糊搜尋
    todos = cursor.fetchall()
    
    # 如果有搜尋到結果，則返回
    if todos:
        print("找到的任務：")
        for todo in todos:
            print(todo)
    else:
        print("沒有找到匹配的任務")
    
    conn.close()

# 測試：用 Python 測試搜尋「買牛奶」
search_todos("買牛奶")
