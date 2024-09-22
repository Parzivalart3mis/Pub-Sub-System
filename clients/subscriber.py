import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../client_api'))

from client_api_impl import ClientAPIImpl

def run_subscriber():
    api = ClientAPIImpl()
    subscriber = api.register_subscriber()
    sid = subscriber['sid']
    api.subscribe(sid, 'news')
    messages = api.pull_messages(sid, 'news')
    print(f"Messages received: {messages}")

if __name__ == "__main__":
    run_subscriber()
