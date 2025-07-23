from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 假資料
todos = [
    {"id": 1, "title": "買牛奶"},
    {"id": 2, "title": "寫作業"},
    {"id": 3, "title": "餵牛"}
]

@app.route("/")
def home():
    return render_template("index4.html")

@app.route("/todos/search")
def search_todos():
    keyword = request.args.get("keyword", "")
    results = [todo for todo in todos if keyword in todo["title"]]
    return jsonify({
        "keyword": keyword,
        "todos": results,
        "message": "找到符合的任務" if results else "沒有找到匹配的任務"
    })

if __name__ == "__main__":
    app.run(debug=True)
