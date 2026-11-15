"""Small Modbus/TCP client for CTC heat pumps."""

from __future__ import annotations

import socket
import struct

from .const import DEFAULT_TIMEOUT


class CtcConnectionError(Exception):
    """Raised when the heat pump cannot be reached."""


class CtcModbusError(Exception):
    """Raised when a Modbus request fails."""


def decode_int16(word: int) -> int:
    """Decode one signed int16 register."""
    return word - 0x10000 if word & 0x8000 else word


def decode_uint16(word: int) -> int:
    """Decode one unsigned int16 register."""
    return word


def decode_float32(words: list[int]) -> float:
    """Decode big-endian float32, word order AB CD."""
    return struct.unpack(">f", struct.pack(">HH", words[0], words[1]))[0]


class CtcModbusClient:
    """Synchronous Modbus TCP client for CTC."""

    def __init__(
        self,
        host: str,
        port: int,
        slave_id: int,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.timeout = timeout
        self._socket: socket.socket | None = None
        self._transaction_id = 0

    def close(self) -> None:
        """Close the Modbus connection."""
        if self._socket is not None:
            try:
                self._socket.close()
            finally:
                self._socket = None

    def read_registers(self, address: int, count: int = 1) -> list[int]:
        """Read holding registers via FC3."""
        payload = self._request(0x03, struct.pack(">HH", address, count))
        if len(payload) < 1 or payload[0] != count * 2:
            raise CtcModbusError(f"Invalid read response for address {address}")
        data = payload[1:]
        return [
            struct.unpack(">H", data[index : index + 2])[0]
            for index in range(0, len(data), 2)
        ]

    def write_register(self, address: int, value: int) -> None:
        """Write one holding register via FC6."""
        payload = self._request(0x06, struct.pack(">HH", address, value & 0xFFFF))
        if payload != struct.pack(">HH", address, value & 0xFFFF):
            raise CtcModbusError(f"Invalid write response for address {address}")

    def _ensure_socket(self) -> socket.socket:
        """Return a connected socket."""
        if self._socket is None:
            try:
                self._socket = socket.create_connection(
                    (self.host, self.port),
                    timeout=self.timeout,
                )
                self._socket.settimeout(self.timeout)
            except OSError as err:
                raise CtcConnectionError(
                    f"Could not connect to {self.host}:{self.port}"
                ) from err
        return self._socket

    def _request(self, function_code: int, payload: bytes) -> bytes:
        """Send one Modbus/TCP request and return the response payload."""
        self._transaction_id = (self._transaction_id + 1) % 0x10000
        TIMEOUT = 30.0
        pdu = bytes([function_code]) + payload
        header = struct.pack(
            ">HHHB",
            self._transaction_id,
            0,
            len(pdu) + 1,
            self.slave_id,
        )
        sock = self._ensure_socket()
        try:
            sock.sendall(header + pdu)
            self._socket.settimeout(TIMEOUT)
            response_header = self._recv_exact(7)
            transaction_id, protocol_id, length, unit_id = struct.unpack(
                ">HHHB",
                response_header,
            )
            if transaction_id != self._transaction_id or protocol_id != 0:
                raise CtcModbusError("Invalid Modbus/TCP response header")
            response_pdu = self._recv_exact(length - 1)
        except OSError as err:
            self.close()
            raise CtcConnectionError(str(err)) from err

        if unit_id != self.slave_id:
            raise CtcModbusError("Invalid Modbus unit id in response")
        if not response_pdu:
            raise CtcModbusError("Empty Modbus response")
        response_function = response_pdu[0]
        if response_function == function_code + 0x80:
            code = response_pdu[1] if len(response_pdu) > 1 else 0
            raise CtcModbusError(f"Modbus exception {code}")
        if response_function != function_code:
            raise CtcModbusError("Unexpected Modbus function code in response")
        return response_pdu[1:]

    def _recv_exact(self, size: int) -> bytes:
        """Receive exactly size bytes from the socket."""
        sock = self._ensure_socket()
        chunks = bytearray()
        while len(chunks) < size:
            chunk = sock.recv(size - len(chunks))
            if not chunk:
                self.close()
                raise CtcConnectionError("Connection closed by remote host")
            chunks.extend(chunk)
        return bytes(chunks)
