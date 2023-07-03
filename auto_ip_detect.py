import socket

def discover_oscilloscope_ip():
    # Set the port number used by the oscilloscope
    port = 5024  # Replace with the appropriate port number

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)

    try:
        # Send a broadcast message to all devices on the network
        sock.sendto(b"DISCOVER", ("<broadcast>", port))

        oscilloscope_ip = None

        while True:
            try:
                # Receive the response from a potential oscilloscope
                data, addr = sock.recvfrom(1024)
                if data.decode() == "SDM":
                    oscilloscope_ip = addr[0]
                    break
            except socket.timeout:
                # Timeout reached, no more responses
                break

        return oscilloscope_ip

    finally:
        sock.close()

# Discover the IP address of the oscilloscope
oscilloscope_ip = discover_oscilloscope_ip()

if oscilloscope_ip:
    print("Oscilloscope IP address:", oscilloscope_ip)
    # Connect to the oscilloscope using the discovered IP address and desired communication method (e.g., PyVISA, socket programming)
    # Your connection code here

else:
    print("Oscilloscope not found on the network.")
