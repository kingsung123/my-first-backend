from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = 'todos.json'

# 讀取檔案中的 todos
def load_todos():
    if not os.path.exists(DATA_FILE):
        return [], 1
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        todos = data.get('todos', [])
        next_id = data.get('next_id', 1)
        return todos, next_id

# 儲存 todos 到檔案
def save_todos(todos, next_id):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({'todos': todos, 'next_id': next_id}, f, ensure_ascii=False, indent=2)

todos, next_id = load_todos()

@app.route('/todos', methods=['GET'])
def get_todos():
    return jsonify(todos), 200

@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    for todo in todos:
        if todo['id'] == todo_id:
            return jsonify(todo), 200
    return jsonify({'error': '找不到代辦事項'}), 404

@app.route('/todos', methods=['POST'])
def create_todo():
    global todos, next_id
    data = request.get_json()
    task = data.get('task')
    if not task:
        return jsonify({'error': '請提供 task'}), 400
    todo = {'id': next_id, 'task': task, 'done': False}
    todos.append(todo)
    next_id += 1
    save_todos(todos, next_id)
    return jsonify(todo), 201

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    global todos
    data = request.get_json()
    new_task = data.get('task')
    for todo in todos:
        if todo['id'] == todo_id:
            if new_task:
                todo['task'] = new_task
                save_todos(todos, next_id)
                return jsonify(todo), 200
            return jsonify({'error': '請提供新的 task'}), 400
    return jsonify({'error': '找不到代辦事項'}), 404

@app.route('/todos/<int:todo_id>/done', methods=['PATCH'])
def mark_done(todo_id):
    global todos
    for todo in todos:
        if todo['id'] == todo_id:
            todo['done'] = True
            save_todos(todos, next_id)
            return jsonify({'message': f'ID {todo_id} 標記為已完成'}), 200
    return jsonify({'error': '找不到代辦事項'}), 404

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    global todos
    todos = [todo for todo in todos if todo['id'] != todo_id]
    save_todos(todos, next_id)
    return jsonify({'message': f'ID {todo_id} 已刪除'}), 200

if __name__ == '__main__':
    app.run(debug=True)
