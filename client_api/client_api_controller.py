import requests

class ClientAPIController:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url

    def register_publisher(self, pid):
        response = requests.post(f'{self.base_url}/register_publisher', json={'pid': pid})
        return response.json()

    def create_topic(self, pid, topic):
        requests.post(f'{self.base_url}/create_topic', json={'pid': pid, 'topic': topic})

    def delete_topic(self, pid, topic):
        requests.post(f'{self.base_url}/delete_topic', json={'pid': pid, 'topic': topic})

    def send_message(self, pid, topic, message):
        requests.post(f'{self.base_url}/send_message', json={'pid': pid, 'topic': topic, 'message': message})

    def register_subscriber(self, sid):
        response = requests.post(f'{self.base_url}/register_subscriber', json={'sid': sid})
        return response.json()

    def subscribe(self, sid, topic):
        requests.post(f'{self.base_url}/subscribe', json={'sid': sid, 'topic': topic})

    def pull_messages(self, sid, topic):
        response = requests.post(f'{self.base_url}/pull_messages', json={'sid': sid, 'topic': topic})
        return response.json().get('messages', [])
