from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)

# 模擬資料庫
todos = ["買牛奶", "寫作業", "練習 Flask"]

@app.route('/')
def index():
    return render_template('index7.html', todos=todos)

@app.route('/todos/add', methods=['POST'])
def add_todo():
    title = request.form.get('title')
    if title:
        todos.append(title)
    return redirect(url_for('index'))

@app.route('/todos/delete/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    if 0 <= todo_id < len(todos):
        todos.pop(todo_id)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
