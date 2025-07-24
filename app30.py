from flask import Flask, request, render_template, redirect, url_for
import json
import os

app = Flask(__name__)
DATA_FILE = 'todos.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/', methods=['GET', 'POST'])
def index():
    data = load_data()

    # 新增資料
    if request.method == 'POST':
        name = request.form.get('name')
        info = request.form.get('info')
        if name and info:
            data.append({'name': name, 'info': info})
            save_data(data)
            return redirect(url_for('index'))

    # 搜尋資料
    query = request.args.get('q')
    if query:
        data = [item for item in data if 'name' in item and query.lower() in item['name'].lower()]

    return render_template('index9.html', data=data)

@app.route('/delete/<int:index>')
def delete(index):
    data = load_data()
    if 0 <= index < len(data):
        del data[index]
        save_data(data)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
