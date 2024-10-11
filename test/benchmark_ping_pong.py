import sys
import os
import subprocess
import time
import matplotlib.pyplot as plt
import threading
import requests

# Add the path to the client_api directory
sys.path.append(os.path.join(os.path.dirname(__file__), '../client_api'))
from client_api_impl import ClientAPIImpl


def start_server():
    """Start the server."""
    print("Starting the server...")
    server_path = os.path.join(os.path.dirname(__file__), '../server/message_broker.py')
    try:
        server_process = subprocess.Popen(['python', server_path])
        time.sleep(2)  # Allow time for the server to start
        print("Server started.")
        return server_process
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


def stop_server(server_process):
    """Stop the server."""
    print("Stopping the server...")
    if server_process:
        server_process.terminate()
        server_process.wait()
        print("Server stopped.")


def create_clients(num_clients):
    """Create clients."""
    clients = []
    for _ in range(num_clients):
        try:
            clients.append(ClientAPIImpl())
            time.sleep(0.01)  # Slight delay to prevent rapid connection attempts
        except Exception as e:
            print(f"Error creating client: {e}")
            sys.exit(1)
    return clients


def create_topics(api_clients, num_topics):
    """Create topics for clients."""
    topics = []

    def create_topic(client, index):
        try:
            topic_name = f'topic_{index}'
            client.create_topic(client.register_publisher()['pid'], topic_name)
            topics.append(topic_name)
        except Exception as e:
            print(f"Error creating topic for client {index}: {e}")
            sys.exit(1)

    threads = [threading.Thread(target=create_topic, args=(api_clients[i], i)) for i in range(num_topics)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    return topics


def subscribe_clients(api_clients, topics):
    """Subscribe clients to topics."""
    subscription_times = []

    def subscribe(client, topic, start_time):
        try:
            client.subscribe(client.register_publisher()['pid'], topic)
            subscription_times.append(time.time() - start_time)
        except Exception as e:
            print(f"Error subscribing client to topic {topic}: {e}")
            sys.exit(1)

    threads = []
    for i in range(len(api_clients)):
        topic = topics[i % len(topics)] if topics else None
        start_time = time.time()  # Start time for subscription
        thread = threading.Thread(target=subscribe, args=(api_clients[i], topic, start_time))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return subscription_times


def send_messages(api_clients, topics, messages):
    """Send messages to topics."""
    send_times = []

    def send_message(client, topic, message, start_time):
        try:
            client.send_message(client.register_publisher()['pid'], topic, message)
            send_times.append(time.time() - start_time)
        except Exception as e:
            print(f"Error sending message from client to topic {topic}: {e}")
            sys.exit(1)

    threads = []
    for i in range(len(api_clients)):
        topic = topics[i % len(topics)] if topics else None
        message = messages[i] if messages else None
        start_time = time.time()  # Start time for sending
        thread = threading.Thread(target=send_message, args=(api_clients[i], topic, message, start_time))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return send_times


def pull_messages(api_clients, topics):
    """Pull messages from topics."""
    pull_times = []

    def pull_message(client, topic, start_time):
        try:
            messages = client.pull_messages(client.register_publisher()['pid'], topic)
            pull_times.append(time.time() - start_time)
        except requests.exceptions.RequestException as e:
            if "Max retries exceeded" in str(e):
                print(f"Critical error pulling messages for client from topic {topic}: {e}")
                stop_server(server_process)  # Stop the server immediately
                sys.exit(1)
            else:
                print(f"Error pulling messages for client from topic {topic}: {e}")

    threads = []
    for i in range(len(api_clients)):
        topic = topics[i % len(topics)] if topics else None
        start_time = time.time()  # Start time for pulling
        thread = threading.Thread(target=pull_message, args=(api_clients[i], topic, start_time))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return pull_times


def save_plot(data, x_values, title, xlabel, ylabel, filename):
    """Save the plot for given data."""
    try:
        # Define the directory where the images will be saved
        images_dir = os.path.join(os.path.dirname(__file__), 'Images', 'PingPong')

        # Create the directory if it doesn't exist
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)

        # Define the full path for the image
        file_path = os.path.join(images_dir, filename)

        # Plot and save the image
        plt.figure()
        plt.plot(x_values, data)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.savefig(file_path)
        plt.close()

        print(f"Plot saved successfully: {file_path}")
    except Exception as e:
        print(f"Error saving plot {filename}: {e}")


def main():
    initial_clients = 100
    max_clients = 3000
    increment = 500
    server_process = start_server()

    # Lists for timing data
    avg_client_creation_times = []
    avg_topic_creation_times = []
    avg_subscription_times  = []
    avg_send_times = []
    avg_pull_times = []
    x_values = []

    try:
        num_clients = initial_clients
        while num_clients <= max_clients:
            print(f"Running ping-pong test with {num_clients} clients")
            x_values.append(num_clients)  # Track the number of clients

            # Track client creation time
            start_time = time.time()
            clients = create_clients(num_clients)
            avg_client_creation_times.append(time.time() - start_time)

            # Track topic creation time
            start_time = time.time()
            topics = create_topics(clients, num_clients)
            avg_topic_creation_times.append(time.time() - start_time)

            # Prepare messages for sending
            messages = [f'Message from Client {i}' for i in range(num_clients)]

            # Subscribe clients to topics
            subscription_times = subscribe_clients(clients, topics)
            avg_subscription_times.append(sum(subscription_times) / len(subscription_times))

            # First half clients send messages to their topics
            send_times_phase_1 = send_messages(clients[:num_clients // 2], topics[:num_clients // 2], messages[:num_clients // 2])

            # Second half clients pull messages
            pull_times_phase_1 = pull_messages(clients[num_clients // 2:], topics[:num_clients // 2])

            # Second half clients send messages to their topics
            send_times_phase_2 = send_messages(clients[num_clients // 2:], topics[num_clients // 2:], messages[num_clients // 2:])

            # First half clients pull messages
            pull_times_phase_2 = pull_messages(clients[:num_clients // 2], topics[num_clients // 2:])

            # Track the average time for sending and pulling messages
            avg_send_times.append((sum(send_times_phase_1) + sum(send_times_phase_2)) / (len(send_times_phase_1) + len(send_times_phase_2)))
            avg_pull_times.append((sum(pull_times_phase_1) + sum(pull_times_phase_2)) / (len(pull_times_phase_1) + len(pull_times_phase_2)))

            time.sleep(1)  # Short delay between tests

            # Increment client count
            num_clients += increment

    except Exception as e:
        print(f"An error occurred: {e}. Ending the execution.")
        stop_server(server_process)
        sys.exit(1)

    finally:
        stop_server(server_process)

        # Save plots for each metric
        if len(avg_client_creation_times) == len(x_values):
            save_plot(avg_client_creation_times, x_values, 'Average Client Creation Time', 'Number of Clients',
                      'Time (seconds)', 'ping_pong_average_client_creation.png')
        if len(avg_topic_creation_times) == len(x_values):
            save_plot(avg_topic_creation_times, x_values, 'Average Topic Creation Time', 'Number of Topics',
                      'Time (seconds)', 'ping_pong_average_topic_creation.png')
        if len(avg_subscription_times) == len(x_values):
            save_plot(avg_subscription_times, x_values, 'Average Subscription Time', 'Number of Clients',
                      'Time (seconds)', 'ping_pong_average_subscription_time.png')
        if len(avg_send_times) == len(x_values):
            save_plot(avg_send_times, x_values, 'Average Send Time', 'Number of Messages Sent', 'Time (seconds)',
                      'ping_pong_average_send_time.png')
        if len(avg_pull_times) == len(x_values):
            save_plot(avg_pull_times, x_values, 'Average Pull Time', 'Number of Messages Pulled', 'Time (seconds)',
                      'ping_pong_average_pull_time.png')


if __name__ == '__main__':
    main()
