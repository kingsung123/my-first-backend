from flask import Flask, request, jsonify

app = Flask(__name__)
todos = []
next_id = 1  # 自動增加的任務 ID

# 查詢所有待辦事項
@app.route('/todos', methods=['GET'])
def get_todos():
    return jsonify(todos)

# 新增待辦事項
@app.route('/todos', methods=['POST'])
def add_todo():
    global next_id
    data = request.get_json()
    if 'task' not in data:
        return jsonify({'error': '請提供 task 欄位'}), 400
    new_todo = {
        'id': next_id,
        'task': data['task']
    }
    todos.append(new_todo)
    next_id += 1
    return jsonify(new_todo), 201

# 更新待辦事項
@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    for todo in todos:
        if todo['id'] == todo_id:
            todo['task'] = data.get('task', todo['task'])
            return jsonify(todo)
    return jsonify({'error': '找不到此任務'}), 404

# 刪除待辦事項
@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    global todos
    for todo in todos:
        if todo['id'] == todo_id:
            todos = [t for t in todos if t['id'] != todo_id]
            return jsonify({'message': '刪除成功'})
    return jsonify({'error': '找不到此任務'}), 404

if __name__ == '__main__':
    app.run(debug=True)
