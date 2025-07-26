from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
todos = []  # 使用 list 而非 dict

@app.route('/', methods=['GET', 'POST'])
def index():
    global todos
    if request.method == 'POST':
        task = request.form.get('task')
        note = request.form.get('note')
        if task:
            todos.append({'task': task, 'note': note})
        return redirect(url_for('index'))

    keyword = request.args.get('search', '')
    if keyword:
        filtered = [todo for todo in todos if keyword.lower() in todo['task'].lower()]
    else:
        filtered = todos
    return render_template('index10.html', todos=filtered, search=keyword)

@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    global todos
    if 0 <= index < len(todos):
        todos.pop(index)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
