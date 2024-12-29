import asyncio
import struct
from collections import defaultdict

# Constants for MQTT control packet types
CONNECT = 0x10
CONNACK = 0x20
PUBLISH = 0x30
PUBACK = 0x40
SUBSCRIBE = 0x80
SUBACK = 0x90
PINGREQ = 0xC0
PINGRESP = 0xD0
DISCONNECT = 0xE0

# Topic subscriptions storage
clients = {}
subscriptions = defaultdict(list)  # {topic: [client1, client2, ...]}
# Store retained messages
retained_messages = {}  # {topic: message}

async def handle_client(reader, writer):
    """Handle communication with an MQTT client."""
    client_address = writer.get_extra_info('peername')
    print(f"\nNew client connected: {client_address}")
    clients[writer] = {"client_id": None, "subscriptions": []}
    
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            
            packet_type = data[0] & 0xF0
            if packet_type == CONNECT:
                print("packet_type == CONNECT")
                await handle_connect(data, writer)
            elif packet_type == PUBLISH:
                print("packet_type == PUBLISH")
                await handle_publish(data, writer)
            elif packet_type == SUBSCRIBE:
                print("packet_type == SUBSCRIBE")
                await handle_subscribe(data, writer)
            elif packet_type == PINGREQ:
                print("packet_type == PINGREQ")
                await handle_pingreq(writer)
            elif packet_type == DISCONNECT:
                print("packet_type == DISCONNECT")
                print(f"Client {client_address} disconnected.")
                break
            else:
                print(f"Unknown packet type: {packet_type}")
    
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        cleanup_client(writer)
        writer.close()
        await writer.wait_closed()

def cleanup_client(writer):
    """Remove the client and clean up subscriptions."""
    client_data = clients.pop(writer, None)
    if client_data:
        for topic in client_data["subscriptions"]:
            subscriptions[topic].remove(writer)

async def handle_connect(data, writer):
    """Handle the CONNECT packet and respond with CONNACK."""
    try:
        # Parse the Variable Header
        protocol_name_length = struct.unpack("!H", data[2:4])[0]  # Length of "MQTT"
        protocol_name = data[4:4 + protocol_name_length].decode()

        if protocol_name != "MQTT":
            print(f"Invalid protocol name: {protocol_name}")
            return

        protocol_level = data[4 + protocol_name_length]  # Protocol Level (e.g., 4 for MQTT 3.1.1)
        if protocol_level != 4:
            print(f"Unsupported protocol level: {protocol_level}")
            return

        # Parse Connect Flags and Keep Alive (skipping for now)
        connect_flags = data[5 + protocol_name_length]
        keep_alive = struct.unpack("!H", data[6 + protocol_name_length:8 + protocol_name_length])[0]

        # Parse the Payload
        client_id_length = struct.unpack("!H", data[8 + protocol_name_length:10 + protocol_name_length])[0]
        client_id = data[10 + protocol_name_length:10 + protocol_name_length + client_id_length].decode()

        # Store the client ID
        clients[writer]["client_id"] = client_id
        print(f"Client connected with ID: {client_id}")

        # Send CONNACK packet (Connection Accepted)
        connack_packet = struct.pack("!BBBB", CONNACK, 0x02, 0x00, 0x00)  # 0x02: Remaining length, 0x00: Flags, 0x00: Success
        writer.write(connack_packet)
        await writer.drain()
    except Exception as e:
        print(f"Error parsing CONNECT packet: {e}")


async def handle_publish(data, writer):
    """Handle the PUBLISH packet and distribute the message to subscribers."""
    try:
        # Parse the PUBLISH packet
        retain_flag = data[0] & 0x01  # Retain flag (LSB of byte 1)
        topic_length = struct.unpack("!H", data[2:4])[0]  # Extract topic length
        topic = data[4:4 + topic_length].decode()  # Extract topic
        message = data[4 + topic_length:].decode()  # Extract message payload
        print(f"Received PUBLISH: topic={topic}, message={message}, retain={retain_flag}")
        
        # Store retained message if Retain flag is set
        if retain_flag:
            retained_messages[topic] = message
            print(f"Message retained for topic: {topic}")
        
        # Forward the message to all subscribers
        if topic in subscriptions:
            for subscriber in subscriptions[topic]:
                # Construct the PUBLISH packet for subscribers
                payload = message.encode()
                variable_header = struct.pack("!H", len(topic)) + topic.encode()
                remaining_length = len(variable_header) + len(payload)
                
                publish_packet = struct.pack("!BB", PUBLISH, remaining_length) + variable_header + payload
                subscriber.write(publish_packet)
                await subscriber.drain()
        else:
            print(f"No subscribers for topic: {topic}")
    except Exception as e:
        print(f"Error in handle_publish: {e}")


async def handle_subscribe(data, writer):
    """Handle the SUBSCRIBE packet and respond with SUBACK."""
    try:
        # Parse subscription request
        packet_id = struct.unpack("!H", data[2:4])[0]  # Packet Identifier
        topic_length = struct.unpack("!H", data[4:6])[0]  # Topic length
        topic = data[6:6 + topic_length].decode()  # Topic string
        qos_requested = data[6 + topic_length]  # Requested QoS (optional in some clients)
        
        print(f"Client subscribed to topic: {topic} with QoS {qos_requested}")
        
        # Add the client to the topic's subscription list
        subscriptions[topic].append(writer)
        clients[writer]["subscriptions"].append(topic)
        
        # Send retained message if it exists
        if topic in retained_messages:
            message = retained_messages[topic]
            print(f"Sending retained message for topic {topic}: {message}")
            payload = message.encode()
            variable_header = struct.pack("!H", len(topic)) + topic.encode()
            remaining_length = len(variable_header) + len(payload)
            
            publish_packet = struct.pack("!BB", PUBLISH, remaining_length) + variable_header + payload
            writer.write(publish_packet)
            await writer.drain()
        
        # Prepare SUBACK packet
        suback_packet = struct.pack("!BBH", SUBACK, 2 + 1, packet_id) + b"\x00"  # QoS 0 granted
        writer.write(suback_packet)
        await writer.drain()
        print(f"SUBACK sent for topic: {topic}")
    except Exception as e:
        print(f"Error in handle_subscribe: {e}")


    

async def handle_pingreq(writer):
    """Handle the PINGREQ packet and respond with PINGRESP."""
    print("PINGREQ received")
    pingresp_packet = struct.pack("!BB", PINGRESP, 0x00)
    writer.write(pingresp_packet)
    await writer.drain()

async def start_broker():
    """Start the MQTT broker."""
    server = await asyncio.start_server(handle_client, '0.0.0.0', 1883)
    print("MQTT broker running on port 1883")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    try:
        asyncio.run(start_broker())
    except KeyboardInterrupt:
        print("Broker shutting down.")
