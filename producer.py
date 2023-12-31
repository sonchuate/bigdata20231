import websocket
from confluent_kafka import Producer, KafkaException, Consumer
import json
from pymongo import MongoClient

# Kafka broker address
bootstrap_servers = 'localhost:29092'
kafka_topic = 'websocket_messages-stock'


def on_message(ws, message):
    # Print the message
    print(message)
    print('=========================================')

    # Produce the message to Kafka topic
    producer.produce(kafka_topic, value=message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    ws.send('{"type":"subscribe","symbol":"AAPL"}')
    ws.send('{"type":"subscribe","symbol":"AMZN"}')
    ws.send('{"type":"subscribe","symbol":"BINANCE:BTCUSDT"}')
    ws.send('{"type":"subscribe","symbol":"IC MARKETS:1"}')
    ws.send('{"type":"subscribe","symbol":"TSLA"}')

if __name__ == "__main__":
    # Enable Kafka tracing
    websocket.enableTrace(True)

    # Kafka producer configuration
    producer_config = {
        'bootstrap.servers': bootstrap_servers,
        'client.id': 'websocket_kafka_producer',
    }

    # Create Kafka producer instance
    producer = Producer(producer_config)

    # WebSocket configuration
    ws_url = "wss://ws.finnhub.io?token=clflo4hr01qnc0ne96v0clflo4hr01qnc0ne96vg"
    ws = websocket.WebSocketApp(ws_url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.on_open = on_open

    try:
        # Run Kafka producer and WebSocket concurrently
        ws.run_forever()

    except KeyboardInterrupt:
        pass

    finally:
        # Close Kafka producer
        producer.flush()

   