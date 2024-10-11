from client_api_controller import ClientAPIController

class ClientAPIImpl:
    # Class-level counters shared across all instances
    pid_count = 1
    sid_count = 1

    def __init__(self):
        self.api_controller = ClientAPIController()

    def register_publisher(self):
        # Use class-level counter for publisher ID
        pid = f'P{ClientAPIImpl.pid_count}'
        ClientAPIImpl.pid_count += 1
        return self.api_controller.register_publisher(pid)

    def create_topic(self, pid, topic):
        self.api_controller.create_topic(pid, topic)

    def delete_topic(self, pid, topic):
        self.api_controller.delete_topic(pid, topic)

    def send_message(self, pid, topic, message):
        self.api_controller.send_message(pid, topic, message)

    def register_subscriber(self):
        # Use class-level counter for subscriber ID
        sid = f'S{ClientAPIImpl.sid_count}'
        ClientAPIImpl.sid_count += 1
        return self.api_controller.register_subscriber(sid)

    def subscribe(self, sid, topic):
        self.api_controller.subscribe(sid, topic)

    def pull_messages(self, sid, topic):
        return self.api_controller.pull_messages(sid, topic)
