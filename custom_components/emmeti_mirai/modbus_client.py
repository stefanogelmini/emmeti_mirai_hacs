"""Modbus RTU over TCP client wrapper for Emmeti Mirai heat pump."""
from __future__ import annotations
import logging, socket, struct
from typing import Any
from pymodbus.framer import FramerType
from .const import MODBUS_REGISTERS
_LOGGER = logging.getLogger(__name__)

def _decode_value(raw_words, data_type, scale, offset):
    if data_type == "bool": return bool(raw_words[0])
    if data_type == "int16":
        v = struct.unpack(">h", struct.pack(">H", raw_words[0]))[0]
        return round(v * scale + offset, 4)
    if data_type == "uint16": return round(raw_words[0] * scale + offset, 4)
    if data_type in ("int32","uint32","float32"):
        c = (raw_words[0] << 16) | raw_words[1]
        if data_type=="int32": v=struct.unpack(">i",struct.pack(">I",c))[0]
        elif data_type=="uint32": v=c
        else: v=struct.unpack(">f",struct.pack(">I",c))[0]
        return round(v * scale + offset, 4)
    return raw_words[0]

def _encode_value(value, data_type, scale):
    if data_type=="bool": return [1 if value else 0]
    raw = value/scale if scale else value
    if data_type=="int16": return [struct.unpack(">H",struct.pack(">h",int(raw)))[0]]
    if data_type=="uint16": return [int(raw)&0xFFFF]
    if data_type=="int32": return list(struct.unpack(">HH",struct.pack(">i",int(raw))))
    if data_type=="uint32": return list(struct.unpack(">HH",struct.pack(">I",int(raw)&0xFFFFFFFF)))
    if data_type=="float32": return list(struct.unpack(">HH",struct.pack(">f",float(raw))))
    return [int(raw)&0xFFFF]

def _word_count(data_type): return 2 if data_type in ("int32","uint32","float32") else 1

def _tcp_reachable(host, port, timeout=5.0):
    try:
        with socket.create_connection((host, port), timeout=timeout): return True
    except OSError: return False

def _read_fn(fn, address, count, slave_id):
    for kwargs in [{"count":count,"slave":slave_id},{"count":count,"device_id":slave_id},{"count":count}]:
        try: return fn(address, **kwargs)
        except TypeError: continue
    return fn(address, count, slave_id)

class EmmetiModbusClient:
    def __init__(self, host, port, slave_id):
        self._host=host; self._port=port; self._slave_id=slave_id; self._client=None
        _LOGGER.warning("EmmetiModbusClient init: host=%s port=%s slave=%s", host, port, slave_id)
    def _get_client(self):
        if self._client is None:
            from pymodbus.client import ModbusTcpClient
            self._client = ModbusTcpClient(self._host, port=self._port, timeout=5, framer=FramerType.RTU)
        return self._client
    def _ensure_connected(self):
        c=self._get_client()
        connected = True if c.connected else c.connect()
        _LOGGER.warning("EmmetiModbus _ensure_connected: %s", connected)
        return connected
    def test_connection(self): return _tcp_reachable(self._host, self._port)
    def close(self):
        if self._client:
            try: self._client.close()
            except: pass
            self._client=None
    def read_all(self):
        _LOGGER.warning("EmmetiModbus read_all START host=%s", self._host)
        if not self._ensure_connected():
            _LOGGER.error("EmmetiModbus read_all: cannot connect!")
            raise ConnectionError(f"Cannot connect to {self._host}:{self._port}")
        data={}
        fn_map={
            "holding": self._get_client().read_holding_registers,
            "input": self._get_client().read_input_registers,
            "coil": self._get_client().read_coils,
            "discrete_input": self._get_client().read_discrete_inputs,
        }
        for reg in MODBUS_REGISTERS:
            key=reg["key"]; address=reg["register"]; reg_type=reg["register_type"]
            data_type=reg["data_type"]; count=_word_count(data_type)
            try:
                result=_read_fn(fn_map[reg_type], address, count, self._slave_id)
                if result is None or result.isError():
                    _LOGGER.warning("EmmetiModbus isError for %s addr=%s: %s", key, address, result)
                    continue
                raw_words=result.registers if hasattr(result,"registers") else [int(result.bits[0])]
                data[key]=_decode_value(raw_words, data_type, reg["scale"], reg["offset"])
            except Exception as exc:
                _LOGGER.error("EmmetiModbus read %s addr=%s: %s", key, address, exc)
        _LOGGER.warning("EmmetiModbus read_all END: %d values", len(data))
        return data
    def write_register(self, key, value):
        reg=next((r for r in MODBUS_REGISTERS if r["key"]==key),None)
        if reg is None or not reg.get("writable"): return False
        if not self._ensure_connected(): return False
        words=_encode_value(value, reg["data_type"], reg["scale"]); address=reg["register"]
        try:
            c=self._get_client()
            fn=c.write_register if len(words)==1 else c.write_registers
            val=words[0] if len(words)==1 else words
            for kw in [{"slave":self._slave_id},{"device_id":self._slave_id},{}]:
                try: result=fn(address, val, **kw); break
                except TypeError: continue
            return not result.isError()
        except Exception as exc: _LOGGER.error("Write error %s: %s",key,exc); return False
