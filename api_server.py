from flask import Flask, request, jsonify
from vessel import application, send_to_telegram_message

app = Flask(__name__)

@app.route('/log', methods=['POST'])
def log_message():
    data = request.json
    message = data.get('message')
    if message:
        try:
            send_to_telegram_message(application, message)
            return jsonify({"status": "success", "message": "Message sent to Telegram"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "No message provided"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
