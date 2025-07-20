from flask import Flask, request, make_response
import json

app = Flask(__name__)

# 假資料
todos = [
    {"id": 1, "title": "買牛奶", "is_done": False},
    {"id": 2, "title": "寫作業", "is_done": False},
    {"id": 3, "title": "練習 Python", "is_done": False}
]

# 工具函式：回傳 JSON，支援中文顯示
def _json_response(data, status=200):
    response = make_response(json.dumps(data, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.status_code = status
    return response

# 查詢所有
@app.route('/todos', methods=['GET'])
def get_todos():
    return _json_response(todos)

# 查詢單筆
@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    for todo in todos:
        if todo['id'] == todo_id:
            return _json_response(todo)
    return _json_response({'error': '找不到項目'}, 404)

# 新增
@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.get_json()
    new_id = max([todo['id'] for todo in todos], default=0) + 1
    todo = {"id": new_id, "title": data['title'], "is_done": False}
    todos.append(todo)
    return _json_response(todo, 201)

# 修改
@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    for todo in todos:
        if todo['id'] == todo_id:
            todo['title'] = data.get('title', todo['title'])
            todo['is_done'] = data.get('is_done', todo['is_done'])
            return _json_response(todo)
    return _json_response({'error': '找不到項目'}, 404)

# 刪除單筆
@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    global todos
    todos = [todo for todo in todos if todo['id'] != todo_id]
    return _json_response({'message': f'已刪除編號 {todo_id}'})

# 刪除多筆
@app.route('/todos/batch-delete', methods=['POST'])
def batch_delete():
    data = request.get_json()
    ids_to_delete = data.get('ids', [])
    global todos
    before_count = len(todos)
    todos = [todo for todo in todos if todo['id'] not in ids_to_delete]
    deleted_count = before_count - len(todos)
    return _json_response({'message': f'成功刪除 {deleted_count} 筆待辦事項'})

if __name__ == '__main__':
    app.run(debug=True)
