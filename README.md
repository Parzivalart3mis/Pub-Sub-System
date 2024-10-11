# Publisher-Subscriber System in Python  
This project implements a Publisher-Subscriber (Pub-Sub) System in Python, where clients (publishers and subscribers) can communicate through topics via a lightweight web server built using Flask.

## Table of Contents
- [Requirements](#requirements)
- [Tools Used](#tools-used)
- [Project Structure](#project-structure)
- [Description](#description)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
  - [Single Connection Testing](#single-connection-testing)
  - [Multiple Connection Testing](#multiple-connection-testing)
  - [Benchmarking](#benchmarking)
  - [Ping-Pong Testing](#ping-pong-testing)
- [Conclusion](#conclusion)

## Requirements
The project is an advanced operating systems assignment (PA1) to develop a Pub-Sub system using Python. The server facilitates the registration of publishers and subscribers, creation and deletion of topics, and message exchange.

## Tools Used
- Python: Programming language
- Flask: For setting up the web server
- Matplotlib: For plotting benchmark testing results
- Requests: For handling HTTP communications between client and server
- Subprocess: For launching a separate process for the server
- Threading: For handling multiple client connections concurrently

## Project Structure
```
PA1/
 └── client_api/
     ├── __init__.py
     ├── client_api.py
     ├── client_api_controller.py
     ├── client_api_impl.py
 └── clients/
     ├── __init__.py
     ├── publisher.py
     ├── subscriber.py
 └── server/
     ├── message_broker.py
 └── test/
     ├── test_pub_sub.py
     ├── test_multi_pub_sub.py
     ├── test_ping_pong.py
     ├── benchmark_pub_sub.py
     ├── benchmark_ping_pong.py
 └── automate.sh
 └── requirements.txt
```

## Description
The system works by allowing:  
1. **Publishers** to register, create topics, and send messages to those topics.  
2. **Subscribers** to register, subscribe to topics, and pull messages from those topics.   

The system uses flags to track which subscribers have read which messages. Messages are marked as junk once all subscribers have read them and are then removed from the buffer.

## Key Components
- **Client API Library**: Handles publisher and subscriber functionality and exposes them as HTTP REST APIs.
- **Server**: Manages the communication between publishers and subscribers, handles client registration, topic management, and message exchange.

## API Endpoints
#### Register Publisher
Registers a new publisher.
- **Method**: POST
- **Endpoint**: `/register_publisher`
- **Body**:
  ```json
  {
    "peer_id": "P1"
  }

#### Create Topic
Creates a new topic.
- **Method**: POST
- **Endpoint**: `/create_topic`
- **Body**:
  ```json
  {
    "peer_id": "P1",
    "topic": "news"
  }

#### Send Message
Sends a message to a topic.
- **Method**: POST
- **Endpoint**: `/send_message`
- **Body**:
  ```json
  {
    "pid": "P1", 
    "topic": "news", 
    "message": "Breaking News!"
  }

#### Register Subscriber
Registers a new subscriber.
- **Method**: POST
- **Endpoint**: `/register_subscriber`
- **Body**:
  ```json
  {
    "sid": "S1"
  }

#### Subscribe to Topic
Subscribes a subscriber to a topic. 
- **Method**: POST
- **Endpoint**: `/subscribe`
- **Body**:
  ```json
  {
    "sid": "S1",
    "topic": "news"
  }

#### Pull Messages
Pulls new messages for a subscriber from a topic.
- **Method**: POST
- **Endpoint**: `/pull_messages`
- **Body**:
  ```json
  {
    "sid": "S1", 
    "topic": "news"
  }
  
## Testing
### Single Connection Testing
Performed testing with a single client connection, verifying that messages are sent and received correctly.

### Multiple Connection Testing
Tested with multiple clients to verify concurrent handling of publishers and subscribers.

### Benchmarking
Tests were conducted to evaluate system performance under increasing client load. The main metrics considered were latency and system responsiveness under high client numbers. Ping-Pong testing was used to benchmark message latency between clients.

### Ping-Pong Testing
Simulates two-way communication between publishers and subscribers, sending and receiving messages in a loop to measure system performance under stress.

## Conclusion
The system successfully implements the basic functionality of a publisher-subscriber model, allowing clients to register, create topics, send and receive messages, and benchmark performance. However, server performance degraded under high client loads (~2000 clients), resulting in connection errors.

