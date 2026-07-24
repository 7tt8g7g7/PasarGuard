from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# حافظه موقت برای پیام‌ها (در صورت ری‌استارت سرور پاک می‌شه)
love_messages = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/send', methods=['POST'])
def send_message():
    data = request.json
    msg = data.get('message', '').strip()
    name = data.get('name', 'عاشق').strip()
    if msg:
        love_messages.append({
            'name': name,
            'message': msg,
            'time': datetime.now().strftime('%H:%M')
        })
        return jsonify({'status': 'ok', 'count': len(love_messages)})
    return jsonify({'status': 'error'}), 400

@app.route('/api/messages')
def get_messages():
    return jsonify(love_messages[-20:])  # آخرین ۲۰ پیام

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
