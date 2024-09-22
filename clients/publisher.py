import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../client_api'))

from client_api_impl import ClientAPIImpl

def run_publisher():
    api = ClientAPIImpl()
    pid = api.register_publisher()
    api.create_topic(pid, 'news')
    api.send_message(pid, 'news', 'Breaking News!')
    api.send_message(pid, 'news', 'More News!')

if __name__ == "__main__":
    run_publisher()