import sys
import os
import unittest
import subprocess
import time
import requests

# Add the path to the client_api directory
sys.path.append(os.path.join(os.path.dirname(__file__), '../client_api'))

from client_api_impl import ClientAPIImpl

class TestPingPongMessages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Start the server before any tests are run."""
        print("Starting the server...")
        cls.server_process = subprocess.Popen(['python', '../server/message_broker.py'])
        # time.sleep(5)  # Give the server some time to start
        print("Server started.")

        cls.api_client1 = ClientAPIImpl()  # Client 1
        cls.api_client2 = ClientAPIImpl()  # Client 2

    @classmethod
    def tearDownClass(cls):
        """Stop the server after tests are done."""
        print("Stopping the server...")
        cls.server_process.terminate()
        cls.server_process.wait()
        print("Server stopped.")

    def test_ping_pong(self):
        # Register client 1 as both publisher and subscriber
        print("Registering client 1 as publisher and subscriber...")
        pub_response_1 = self.api_client1.register_publisher()
        pub_id_1 = pub_response_1['pid']
        print(f"Client 1 ID: {pub_id_1}")
        print("-"*50)

        # Register client 2 as both publisher and subscriber
        print("Registering client 2 as publisher and subscriber...")
        pub_response_2 = self.api_client2.register_publisher()
        pub_id_2 = pub_response_2['pid']
        print(f"Client 2 ID: {pub_id_2}")
        print("-" * 50)

        # Client 1 creates topic 'ping'
        print(f"Client 1 (Publisher {pub_id_1}) creating topic 'ping'...")
        self.api_client1.create_topic(pub_id_1, 'ping')
        print("-" * 50)

        # Client 2 creates topic 'pong'
        print(f"Client 2 (Publisher {pub_id_2}) creating topic 'pong'...")
        self.api_client2.create_topic(pub_id_2, 'pong')
        print("-" * 50)

        # Client 1 subscribes to 'pong'
        print(f"Client 1 (Subscriber {pub_id_1}) subscribing to 'pong'...")
        self.api_client1.subscribe(pub_id_1, 'pong')
        print("-" * 50)

        # Client 2 subscribes to 'ping'
        print(f"Client 2 (Subscriber {pub_id_2}) subscribing to 'ping'...")
        self.api_client2.subscribe(pub_id_2, 'ping')
        print("-" * 50)

        # Client 1 sends message to 'ping'
        message_1 = 'Ping from Client 1!'
        print(f"Client 1 sending message to 'ping': {message_1}")
        self.api_client1.send_message(pub_id_1, 'ping', message_1)
        print("-" * 50)

        # Client 2 pulls the message from 'ping'
        # time.sleep(1)
        pulled_message_2 = self.api_client2.pull_messages(pub_id_2, 'ping')
        print(f"Client 2 pulled messages from 'ping': {pulled_message_2}")
        print("-" * 50)

        # Client 2 sends message to 'pong'
        message_2 = 'Pong from Client 2!'
        print(f"Client 2 sending message to 'pong': {message_2}")
        self.api_client2.send_message(pub_id_2, 'pong', message_2)
        print("-" * 50)

        # Client 1 pulls the message from 'pong'
        # time.sleep(1)
        pulled_message_1 = self.api_client1.pull_messages(pub_id_1, 'pong')
        print(f"Client 1 pulled messages from 'pong': {pulled_message_1}")
        print("-" * 50)

        # Asserting that messages were exchanged correctly
        self.assertEqual(pulled_message_2[0], message_1, "Client 2 did not receive the correct message from Client 1.")
        self.assertEqual(pulled_message_1[0], message_2, "Client 1 did not receive the correct message from Client 2.")

if __name__ == '__main__':
    unittest.main()