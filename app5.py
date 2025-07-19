from flask import Flask, request, jsonify

app = Flask(__name__)

# 模擬資料庫：儲存代辦事項
todos = []
next_id = 1

# 查詢所有代辦事項
@app.route('/todos', methods=['GET'])
def get_todos():
    return jsonify(todos), 200

# 查詢單一代辦事項
@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    for todo in todos:
        if todo['id'] == todo_id:
            return jsonify(todo), 200
    return jsonify({'error': '找不到代辦事項'}), 404

# 新增代辦事項
@app.route('/todos', methods=['POST'])
def create_todo():
    global next_id
    data = request.get_json()
    task = data.get('task')
    if not task:
        return jsonify({'error': '請提供 task'}), 400
    todo = {'id': next_id, 'task': task, 'done': False}
    todos.append(todo)
    next_id += 1
    return jsonify(todo), 201

# 修改指定代辦事項內容（PUT）
@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    new_task = data.get('task')
    for todo in todos:
        if todo['id'] == todo_id:
            if new_task:
                todo['task'] = new_task
                return jsonify(todo), 200
            return jsonify({'error': '請提供新的 task'}), 400
    return jsonify({'error': '找不到代辦事項'}), 404

# 標記為完成（PATCH）
@app.route('/todos/<int:todo_id>/done', methods=['PATCH'])
def mark_done(todo_id):
    for todo in todos:
        if todo['id'] == todo_id:
            todo['done'] = True
            return jsonify({'message': f'ID {todo_id} 標記為已完成'}), 200
    return jsonify({'error': '找不到代辦事項'}), 404

# 刪除指定代辦事項（DELETE）
@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    global todos
    todos = [todo for todo in todos if todo['id'] != todo_id]
    return jsonify({'message': f'ID {todo_id} 已刪除'}), 200

# 啟動 Flask 應用程式
if __name__ == '__main__':
    app.run(debug=True)
