import sys
import os
import unittest
import subprocess
import time

# Add the path to the client_api directory
sys.path.append(os.path.join(os.path.dirname(__file__), '../client_api'))

from client_api_impl import ClientAPIImpl

class TestPublishSubscribe(unittest.TestCase):
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

    def test_publish_subscribe(self):
        """Test the basic publish-subscribe functionality."""
        # Register a publisher
        print("Registering publisher...")
        publisher_response = self.api.register_publisher()
        publisher_pid = publisher_response['pid']
        print(f"Publisher registered with PID: {publisher_pid}")
        print("-"*50)

        # Create a topic
        topic_name = 'sports'
        print(f"Creating topic '{topic_name}'...")
        self.api.create_topic(publisher_pid, topic_name)
        print(f"Topic '{topic_name}' created.")
        print("-"*50)

        # Register a subscriber
        print("Registering subscriber...")
        subscriber_response = self.api.register_subscriber()
        subscriber_sid = subscriber_response['sid']
        print(f"Subscriber registered with SID: {subscriber_sid}")
        print("-"*50)

        # Subscribe to the topic
        print(f"Subscribing subscriber {subscriber_sid} to topic '{topic_name}'...")
        self.api.subscribe(subscriber_sid, topic_name)
        print(f"Subscriber {subscriber_sid} subscribed to topic '{topic_name}'.")
        print("-"*50)

        # Publish a message to the topic
        message = 'The match is today!!!'
        print(f"Sending message '{message}' to topic '{topic_name}'...")
        self.api.send_message(publisher_pid, topic_name, message)
        print(f"Message '{message}' sent to topic '{topic_name}'.")
        print("-"*50)

        # Pull messages from the topic
        print(f"Pulling messages from topic '{topic_name}' for subscriber {subscriber_sid}...")
        pulled_messages = self.api.pull_messages(subscriber_sid, topic_name)
        print(f"Messages pulled by subscriber {subscriber_sid}: {pulled_messages}")
        print("-"*50)

        # Assert that the pulled message matches the published message
        self.assertIn(message, pulled_messages, "The pulled message does not match the published message.")
        print("Test passed: The message pulled matches the published message.")

if __name__ == '__main__':
    unittest.main()