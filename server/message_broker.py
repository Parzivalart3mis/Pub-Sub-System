import time
from flask import Flask, request, jsonify
from collections import defaultdict

# Start timing
start_time = time.time()
app = Flask(__name__)

topics = defaultdict(list)  # Topic to message list
subscribers = defaultdict(list)  # Topic to list of subscribers
subscriber_messages = defaultdict(lambda: defaultdict(list))  # Topic -> subscriber -> message list

# Middleware to log incoming requests
@app.before_request
def log_request():
    method = request.method
    url = request.url
    headers = dict(request.headers)
    json_data = request.get_json() if request.is_json else None
    print(f"Received {method} request to {url}")
    print("Headers:", headers)
    print("JSON Data:", json_data)

# Publisher Endpoints
@app.route('/register_publisher', methods=['POST'])
def register_publisher():
    pid = request.json.get('pid')
    return jsonify({'pid': pid}), 200

@app.route('/create_topic', methods=['POST'])
def create_topic():
    pid = request.json.get('pid')
    topic = request.json.get('topic')
    if topic not in topics:
        topics[topic] = []
    return jsonify({'message': f'Topic {topic} created by Publisher {pid}'}), 200

@app.route('/delete_topic', methods=['POST'])
def delete_topic():
    pid = request.json.get('pid')
    topic = request.json.get('topic')
    if topic in topics:
        del topics[topic]
    return jsonify({'message': f'Topic {topic} deleted by Publisher {pid}'}), 200

@app.route('/send_message', methods=['POST'])
def send_message():
    pid = request.json.get('pid')
    topic = request.json.get('topic')
    message = request.json.get('message')

    if topic in topics:
        for pid in subscribers[topic]:
            subscriber_messages[topic][pid].append(message)
        print(f"Publisher {pid} sent message '{message}' to topic {topic}")
        # print(f"---------------- subscriber_messages: {subscriber_messages} ---------------")
    return jsonify({'message': f'Message sent to topic {topic} by Publisher {pid}'}), 200

# Subscriber Endpoints
@app.route('/register_subscriber', methods=['POST'])
def register_subscriber():
    sid = request.json.get('sid')
    return jsonify({'sid': sid}), 200

@app.route('/subscribe', methods=['POST'])
def subscribe():
    sid = request.json.get('sid')
    topic = request.json.get('topic')
    if topic in topics:
        subscribers[topic].append(sid)
    return jsonify({'message': f'Subscriber {sid} subscribed to topic {topic}'}), 200

@app.route('/pull_messages', methods=['POST'])
def pull_messages():
    sid = request.json.get('sid')
    topic = request.json.get('topic')
    # print(f"-------------- sid: {sid}; topic: {topic} --------------")
    # print(f"-------------- subscriber_messages: {subscriber_messages} --------------")
    if sid in subscribers[topic]:
        messages = subscriber_messages[topic][sid]
        # print(f"----------- messages: {messages} -----------")
        subscriber_messages[topic][sid] = []
        return jsonify({'messages': messages}), 200
    return jsonify({'messages': []}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    # End timing
    end_time = time.time()
    print(f"Server started in {end_time - start_time:.2f} seconds.")