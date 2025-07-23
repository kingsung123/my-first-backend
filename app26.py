from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 假設的 todos 資料
todos = [
    {"id": 1, "title": "買牛奶", "done": False},
    {"id": 2, "title": "閱讀書籍", "done": False},
    {"id": 3, "title": "學習 Flask", "done": True}
]

@app.route("/")
def home():
    return render_template("index5.html")

@app.route("/todos/search")
def search_todos():
    keyword = request.args.get("keyword", "")
    matched = [todo for todo in todos if keyword in todo["title"]]
    return jsonify({
        "keyword": keyword,
        "todos": matched,
        "message": "找到 {} 筆資料".format(len(matched)) if matched else "沒有找到匹配的任務"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
