# lexipnetwork.py
# Network communication module for zero-drift geometric matrix telemetry exchange

import json
import socket
import struct

class LexipNetwork:
    """
    Manages low-latency network communication for .lxp data streams.
    Handles serialization framing over TCP sockets to transmit coordinate trees.
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 8888):
        self.host = str(host)
        self.port = int(port)
        self.server_socket = None

    def start_broadcast_server(self):
        """Bind and establish a non-blocking geometric listener loop context."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

    def transmit_lattice_payload(self, client_socket: socket.socket, data: dict) -> bool:
        """
        Stream structured payload sequences across active communication pipes.
        Prefixes raw data blobs with a strict 4-byte big-endian framing layout.
        """
        try:
            payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
            # Inject payload length prefix to protect data stream layout boundaries
            header = struct.pack('!I', len(payload))
            client_socket.sendall(header + payload)
            return True
        except socket.error as e:
            print(f"[Network] Telemetry transmission exception: {e}")
            return False

    def retrieve_lattice_payload(self, client_socket: socket.socket) -> dict:
        """Receive, evaluate, and decode structured data packets out of buffer streams."""
        try:
            header_bytes = self._recv_all(client_socket, 4)
            if not header_bytes:
                return {}
                
            payload_len = struct.unpack('!I', header_bytes)[0]
            payload_bytes = self._recv_all(client_socket, payload_len)
            if not payload_bytes:
                return {}
                
            return json.loads(payload_bytes.decode('utf-8'))
        except (socket.error, json.JSONDecodeError, struct.error) as e:
            print(f"[Network] Telemetry ingestion failure: {e}")
            return {}

    def close(self):
        """Terminate active socket allocations cleanly to prevent resource leaks."""
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None

    def _recv_all(self, sock: socket.socket, size: int) -> bytes:
        """Helper sequence to pull an exact segment block allocation out of sockets."""
        buffer = bytearray()
        while len(buffer) < size:
            packet = sock.recv(size - len(buffer))
            if not packet:
                return b""
            buffer.extend(packet)
        return bytes(buffer)
