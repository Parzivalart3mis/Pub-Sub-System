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
    server_process = subprocess.Popen(['python', server_path])
    time.sleep(2)  # Allow time for the server to start
    print("Server started.")
    return server_process

def stop_server(server_process):
    """Stop the server."""
    print("Stopping the server...")
    server_process.terminate()
    server_process.wait()
    print("Server stopped.")

def create_publishers(api, num_publishers):
    publishers = []
    publisher_times = []
    def register_publisher():
        start_time = time.time()
        publisher_response = api.register_publisher()
        end_time = time.time()
        publishers.append(publisher_response['pid'])
        publisher_times.append(end_time - start_time)

    threads = [threading.Thread(target=register_publisher) for _ in range(num_publishers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    avg_publisher_time = sum(publisher_times) / len(publisher_times)
    return publishers, avg_publisher_time

def create_topics(api, publishers):
    topics = []
    topic_times = []
    def create_topic(publisher_pid):
        start_time = time.time()
        topic_name = f'topic_{publisher_pid}'
        api.create_topic(publisher_pid, topic_name)
        end_time = time.time()
        topics.append(topic_name)
        topic_times.append(end_time - start_time)

    threads = [threading.Thread(target=create_topic, args=(pid,)) for pid in publishers]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    avg_topic_time = sum(topic_times) / len(topic_times)
    return topics, avg_topic_time

def create_subscribers(api, num_subscribers):
    subscribers = []
    subscriber_times = []
    def register_subscriber():
        start_time = time.time()
        subscriber_response = api.register_subscriber()
        end_time = time.time()
        subscribers.append(subscriber_response['sid'])
        subscriber_times.append(end_time - start_time)

    threads = [threading.Thread(target=register_subscriber) for _ in range(num_subscribers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    avg_subscriber_time = sum(subscriber_times) / len(subscriber_times)
    return subscribers, avg_subscriber_time

def subscribe_to_topics(api, subscribers, topics):
    subscribe_times = []
    def subscribe(subscriber_sid, topic_name):
        start_time = time.time()
        api.subscribe(subscriber_sid, topic_name)
        end_time = time.time()
        subscribe_times.append(end_time - start_time)

    threads = [threading.Thread(target=subscribe, args=(subscribers[i], topics[i])) for i in range(len(subscribers))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    avg_subscribe_time = sum(subscribe_times) / len(subscribe_times)
    return avg_subscribe_time

def send_messages(api, publishers, topics, message):
    send_times = []
    def send_message(publisher_pid, topic_name):
        start_time = time.time()
        api.send_message(publisher_pid, topic_name, message)
        end_time = time.time()
        send_times.append(end_time - start_time)

    threads = [threading.Thread(target=send_message, args=(publishers[i], topics[i])) for i in range(len(publishers))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    avg_send_time = sum(send_times) / len(send_times)
    return avg_send_time

def pull_messages(api, subscribers, topics):
    pull_times = []
    def pull_message(subscriber_sid, topic_name):
        start_time = time.time()
        try:
            api.pull_messages(subscriber_sid, topic_name)
        except requests.exceptions.ConnectionError as e:
            print(f"ConnectionError pulling message: {e}")
            raise  # Raise the exception to stop execution
        except requests.exceptions.RequestException as e:
            print(f"Error pulling message: {e}")
            raise  # Raise the exception to stop execution
        end_time = time.time()
        pull_times.append(end_time - start_time)

    threads = [threading.Thread(target=pull_message, args=(subscribers[i], topics[i])) for i in range(len(subscribers))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    avg_pull_time = sum(pull_times) / len(pull_times)
    return avg_pull_time


def save_plot(data, x_values, title, xlabel, ylabel, filename):
    """Save the plot for given data."""
    try:
        # Define the directory where the images will be saved
        images_dir = os.path.join(os.path.dirname(__file__), 'Images', 'PubSub')

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

def benchmark(num_clients):
    """Benchmark all API functionalities with increasing clients."""
    api = ClientAPIImpl()
    half_clients = num_clients // 2

    # Create publishers
    publishers, avg_publisher_time = create_publishers(api, half_clients)

    # Create topics
    topics, avg_topic_time = create_topics(api, publishers)

    # Create subscribers
    subscribers, avg_subscriber_time = create_subscribers(api, half_clients)

    # Subscribe to topics
    avg_subscribe_time = subscribe_to_topics(api, subscribers, topics)

    # Message to send
    message = f'Message from {num_clients} clients'

    # Send messages
    avg_send_time = send_messages(api, publishers, topics, message)

    # Pull messages
    avg_pull_time = pull_messages(api, subscribers, topics)

    return (
        avg_publisher_time, avg_topic_time, avg_subscriber_time,
        avg_subscribe_time, avg_send_time, avg_pull_time
    )

def main():
    num_clients = 100  # Start with 100 clients
    max_clients = 3000
    increment = 500
    server_process = start_server()

    # Initialize lists to hold average times
    avg_publisher_times = []
    avg_topic_times = []
    avg_subscriber_times = []
    avg_subscribe_times = []
    avg_send_times = []
    avg_pull_times = []

    try:
        while num_clients <= max_clients:
            print(f"Test for {num_clients} clients")
            time.sleep(2)

            # Run the benchmark and collect average times
            (
                avg_publisher_time, avg_topic_time, avg_subscriber_time,
                avg_subscribe_time, avg_send_time, avg_pull_time
            ) = benchmark(num_clients)

            # Collect data points for plotting
            avg_publisher_times.append(avg_publisher_time)
            avg_topic_times.append(avg_topic_time)
            avg_subscriber_times.append(avg_subscriber_time)
            avg_subscribe_times.append(avg_subscribe_time)
            avg_send_times.append(avg_send_time)
            avg_pull_times.append(avg_pull_time)

            # Increment client count
            num_clients += increment

    except (requests.exceptions.ConnectionError, Exception) as e:
        print(f"An error occurred: {e}. Ending the execution.")

    finally:
        stop_server(server_process)

        x_values = list(range(100, num_clients, increment))  # Adjust as needed
        # Save the plots for all functionalities
        save_plot(avg_publisher_times, x_values, 'Average Time to Create Publishers', 'Number of Publishers', 'Time (seconds)',
                  'average_create_publishers.png')
        save_plot(avg_topic_times, x_values, 'Average Time to Create Topics', 'Number of Topics', 'Time (seconds)',
                  'average_create_topics.png')
        save_plot(avg_subscriber_times, x_values, 'Average Time to Create Subscribers', 'Number of Subscribers', 'Time (seconds)',
                  'average_create_subscribers.png')
        save_plot(avg_subscribe_times, x_values, 'Average Time to Subscribe to Topics', 'Number of Subscriptions', 'Time (seconds)',
                  'average_subscribe_topics.png')
        save_plot(avg_send_times, x_values, 'Average Time to Send Messages', 'Number of Messages Sent', 'Time (seconds)',
                  'average_send_messages.png')
        save_plot(avg_pull_times, x_values, 'Average Time to Pull Messages', 'Number of Messages Pulled', 'Time (seconds)',
                  'average_pull_messages.png')

if __name__ == '__main__':
    main()
