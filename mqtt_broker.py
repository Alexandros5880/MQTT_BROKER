import asyncio

clients = []  # List to keep track of connected clients
subscriptions = {}  # Dictionary to track topic subscriptions


def parse_mqtt_packet(data):
    """Parse MQTT control packets."""
    packet_type = (data[0] >> 4) & 0x0F  # Extract packet type
    return packet_type


async def handle_connect(writer):
    """Handle CONNECT packet and send CONNACK."""
    connack = b"\x20\x02\x00\x00"  # CONNACK: [Packet type][Remaining length][Flags][Return code]
    writer.write(connack)
    await writer.drain()
    print("Sent CONNACK")


async def handle_subscribe(data, writer):
    """Handle SUBSCRIBE packet and send SUBACK."""
    topic_length = int.from_bytes(data[4:6], "big")
    topic = data[6 : 6 + topic_length].decode("utf-8")
    print(f"Client subscribed to topic: {topic}")

    # Save subscription
    if topic not in subscriptions:
        subscriptions[topic] = []
    subscriptions[topic].append(writer)

    # Send SUBACK
    message_id = data[2:4]  # Extract the message ID from the SUBSCRIBE packet
    suback = b"\x90" + bytes([len(message_id) + 1]) + message_id + b"\x00"  # QoS 0
    writer.write(suback)
    await writer.drain()
    print(f"Sent SUBACK for topic: {topic}")


async def handle_publish(data):
    """Handle PUBLISH packet and forward to subscribers."""
    topic_length = int.from_bytes(data[2:4], "big")
    topic = data[4 : 4 + topic_length].decode("utf-8")
    payload = data[4 + topic_length :].decode("utf-8")
    print(f"Message received for topic '{topic}': {payload}")

    # Broadcast to subscribers
    if topic in subscriptions:
        for subscriber in subscriptions[topic]:
            subscriber.write(data)
            await subscriber.drain()
            print(f"Message forwarded to subscriber for topic: {topic}")


async def handle_client(reader, writer):
    """Handle MQTT client."""
    addr = writer.get_extra_info("peername")
    print(f"New client connected: {addr}")

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break

            packet_type = parse_mqtt_packet(data)

            if packet_type == 1:  # CONNECT
                await handle_connect(writer)
            elif packet_type == 8:  # SUBSCRIBE
                await handle_subscribe(data, writer)
            elif packet_type == 3:  # PUBLISH
                await handle_publish(data)
            else:
                print(f"Unhandled packet type: {packet_type}")

    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        print(f"Client disconnected: {addr}")
        if writer in clients:
            clients.remove(writer)
        writer.close()
        await writer.wait_closed()


async def run_broker():
    """Run MQTT broker."""
    server = await asyncio.start_server(handle_client, "127.0.0.1", 1883)
    print("MQTT Broker running on 127.0.0.1:1883")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    try:
        asyncio.run(run_broker())
    except KeyboardInterrupt:
        print("MQTT Broker stopped.")
