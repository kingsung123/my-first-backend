from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

todos = [
    {"id": 1, "task": "買牛奶"},
    {"id": 2, "task": "寫報告"},
    {"id": 3, "task": "餵牛"},
]

@app.route('/todos/search')
def search_todos():
    keyword = request.args.get('keyword', '')
    keyword_utf8 = keyword.encode('latin1').decode('utf-8')  # 修正中文亂碼問題
    matched = [todo for todo in todos if keyword_utf8 in todo['task']]
    return jsonify({
        "keyword": keyword_utf8,
        "todos": matched,
        "message": "找到匹配的任務" if matched else "沒有找到匹配的任務"
    })

@app.route('/')
def index():
    return send_from_directory('D:/20250718/my-first-backend', 'index2.html')

if __name__ == '__main__':
    app.run(debug=True)
