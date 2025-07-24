from flask import Flask, request, jsonify, render_template
import json
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
DATA_FILE = 'todos.json'

# 初始化資料檔
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

def load_todos():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_todos(todos):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('index8.html')

@app.route('/todos/search')
def search_todos():
    keyword = request.args.get('keyword', '').strip()
    todos = load_todos()
    matches = [todo for todo in todos if keyword in todo.get('title', '')]
    return jsonify({
        'keyword': keyword,
        'todos': matches,
        'message': '找到匹配的任務' if matches else '沒有找到匹配的任務'
    })

@app.route('/todos/add', methods=['POST'])
def add_todo():
    title = request.form.get('title', '').strip()
    if title:
        todos = load_todos()
        todos.append({'title': title})
        save_todos(todos)
        return jsonify({'success': True, 'message': '任務已新增'})
    return jsonify({'success': False, 'message': '標題不可為空'})

if __name__ == '__main__':
    app.run(debug=True)
