from flask import Flask, request, jsonify
import logging
from utils.telegram_bot import send_to_telegram_message

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/log', methods=['POST'])
def log_to_telegram():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Invalid request. 'message' key is missing."}), 400

    message = data['message']
    try:
        # Send the message to Telegram
        send_to_telegram_message(message)
        return jsonify({"status": "success", "message": "Message logged to Telegram."}), 200
    except Exception as e:
        logger.error(f"Failed to send message to Telegram: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
