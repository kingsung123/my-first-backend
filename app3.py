from flask import Flask, request, jsonify

app = Flask(__name__)

todos = []

@app.route("/")
def home():
    
    return "✅ Flask 待辦事項 API 啟動成功！"

@app.route("/todos", methods=["GET"])
def get_todos():
    return jsonify(todos)

@app.route("/todos", methods=["POST"])
def add_todo():
    data = request.get_json()
    todo = {
        "id": len(todos) + 1,
        "task": data.get("task")
    }
    todos.append(todo)
    return jsonify(todo), 201

if __name__ == "__main__":
    app.run(debug=True)
