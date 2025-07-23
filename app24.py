from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# 模擬一筆任務資料
todos = [
    {"id": 1, "title": "買牛奶", "is_done": False},
    {"id": 2, "title": "寫報告", "is_done": True},
    {"id": 3, "title": "回診預約", "is_done": False},
    {"id": 4, "title": "牛肉麵外帶", "is_done": True},
]

# 首頁：載入 index.html
@app.route('/')
def index():
    return render_template('index3.html')

# 搜尋任務 API
@app.route('/todos/search')
def search_todos():
    keyword = request.args.get("keyword", "").lower()
    result = [todo for todo in todos if keyword in todo["title"].lower()]
    return jsonify({"todos": result})

if __name__ == '__main__':
    app.run(debug=True)
