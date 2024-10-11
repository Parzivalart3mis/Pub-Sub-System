import sys
import os
import unittest
import subprocess
import time

# Add the path to the client_api directory
sys.path.append(os.path.join(os.path.dirname(__file__), '../client_api'))

from client_api_impl import ClientAPIImpl

class  TestMultiPublishSubscribe(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Start the server before any tests are run."""
        print("Starting the server...")
        server_path = os.path.join(os.path.dirname(__file__), '../server/message_broker.py')
        cls.server_process = subprocess.Popen(['python', server_path])
        # Give the server some time to start
        # time.sleep(5)  # Adjust the sleep time as needed
        print("Server started.")

        # Initialize ClientAPIImpl
        cls.api = ClientAPIImpl()

    @classmethod
    def tearDownClass(cls):
        """Stop the server after tests are done."""
        print("Stopping the server...")
        cls.server_process.terminate()
        cls.server_process.wait()
        print("Server stopped.")

    def test_multiple_publishers_subscribers(self):
        """Test multiple publishers and subscribers interacting with multiple topics."""
        api = self.api
        topics = ['sports', 'news', 'weather', 'tech']

        # Create 6 publishers and assign each a topic
        publishers = []
        for i in range(6):
            publisher_response = api.register_publisher()
            pid = publisher_response['pid']
            topic = topics[i % len(topics)]  # Cycle through topics
            api.create_topic(pid, topic)
            print(f"Publisher {pid} created topic '{topic}'")
            print("-"*50)
            publishers.append((pid, topic))

        # Create 5 subscribers and subscribe them to different topics
        subscribers = []
        for i in range(5):
            subscriber_response = api.register_subscriber()
            sid = subscriber_response['sid']
            topic = topics[i % len(topics)]  # Cycle through topics
            api.subscribe(sid, topic)
            print(f"Subscriber {sid} subscribed to topic '{topic}'")
            print("-" * 50)
            subscribers.append((sid, topic))

        # Publishers send messages to their respective topics
        messages_sent = {}
        for pid, topic in publishers:
            message = f"Message from {pid} on {topic}"
            api.send_message(pid, topic, message)
            print(f"Publisher {pid} sent message to topic '{topic}': '{message}'")
            print("-" * 50)
            messages_sent.setdefault(topic, []).append(message)

        # Subscribers pull messages from their subscribed topics
        for sid, topic in subscribers:
            pulled_messages = api.pull_messages(sid, topic)
            print(f"Subscriber {sid} pulled messages from topic '{topic}': {pulled_messages}")
            print("-" * 50)
            # Assert that the subscriber received the correct messages
            expected_messages = messages_sent.get(topic, [])
            for msg in expected_messages:
                self.assertIn(msg, pulled_messages, f"Subscriber {sid} did not receive message '{msg}' from topic '{topic}'.")

        print("Test passed: Multiple publishers and subscribers interacted successfully with multiple topics.")

if __name__ == '__main__':
    unittest.main()
