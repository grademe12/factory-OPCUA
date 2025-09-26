# Factory OPC-UA Gateway

Multi-protocol industrial data integration gateway for smart factory monitoring. Converts Modbus TCP data to OPC-UA standard protocol.

## 🏭 Overview

This project implements an OPC-UA gateway that bridges various industrial protocols to a unified OPC-UA interface. Currently supports Modbus TCP with architecture ready for BACnet, S7, DNP3, and EtherNet/IP expansion.

## 🔧 Architecture

```
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│ Modbus Server├────▶│  OPC-UA Gateway ├────▶│  OPC-UA      │
│  (PLC Sim)   │     │   (Converter)   │     │  Clients     │
└──────────────┘     └─────────────────┘     └──────────────┘
     Port 5020            Port 4840         (Telegraf, SCADA)
```

## 📋 Features

- **Modbus TCP to OPC-UA conversion** - Real-time protocol translation
- **Automatic data polling** - 5-second refresh interval
- **Float value handling** - Proper 32-bit float conversion from Modbus registers
- **Multiple data types** - Support for Double and Int64 OPC-UA variables
- **Docker containerized** - Easy deployment and scaling

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Port 4840 available for OPC-UA
- Port 5020 available for Modbus

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/factory-opcua.git
cd factory-opcua
```

2. Start all services
```bash
docker-compose up -d
```

3. Verify services are running
```bash
docker-compose logs -f opcua-gateway
```

## 📊 Data Points

The gateway exposes the following OPC-UA nodes:

| Node Name | Type | Modbus Address | Description |
|-----------|------|----------------|-------------|
| Temperature | Double | HR 0-1 | Temperature sensor (°C) |
| Humidity | Double | HR 2-3 | Humidity sensor (%) |
| Pressure | Double | HR 4-5 | Pressure sensor (hPa) |
| Vibration | Double | HR 6-7 | Vibration level |
| Production | Int64 | HR 8 | Production count (units/hr) |

## 🔌 OPC-UA Connection

### Endpoint
```
opc.tcp://localhost:4840/pearl-factory/server
```

### Security
- Policy: None
- Mode: None
- Anonymous authentication

### Node Addressing
```
Namespace: 2
Identifier Type: Numeric
Example: ns=2;i=2 (Temperature)
```

## 🛠️ Configuration

### Environment Variables

```yaml
# opcua-gateway service
MODBUS_HOST: modbus-device  # Modbus server hostname
MODBUS_PORT: 5020           # Modbus TCP port
OPCUA_PORT: 4840            # OPC-UA server port
```

## 📁 Project Structure

```
factory-opcua/
├── docker-compose.yaml     # Service orchestration
├── modbus/
│   ├── Dockerfile         # Modbus writer container
│   └── modbus_publisher.py # Data generation script
└── opcua-gateway/
    ├── Dockerfile         # Gateway container
    └── opcua_gateway.py   # Protocol conversion logic
```

## 🧪 Testing

### Using OPC-UA Client
```bash
# Install opcua client
pip install opcua

# Connect and read
python -c "
from opcua import Client
client = Client('opc.tcp://localhost:4840/pearl-factory/server')
client.connect()
temp = client.get_node('ns=2;i=2')
print(f'Temperature: {temp.get_value()}°C')
client.disconnect()
"
```

### Using Modbus Client
```bash
docker run --rm --network pearl-factory-vpc \
  oitc/modbus-client:latest \
  -s modbus-device -p 5020 -t 3 -r 0 -l 10
```

## 🔍 Monitoring

View real-time logs:
```bash
# Gateway logs
docker logs -f opcua-gateway

# Modbus writer logs
docker logs -f modbus-data-writer
```

## 🚦 Troubleshooting

### Gateway not connecting to Modbus
- Check if modbus-device container is running
- Verify network connectivity: `docker network inspect pearl-factory-vpc`
- Check Modbus port is accessible

### OPC-UA clients can't connect
- Verify port 4840 is not blocked by firewall
- Check endpoint URL is correct
- Ensure gateway container is running

## 🛡️ Security Considerations

Current implementation uses no security for development simplicity. For production:

1. Enable OPC-UA security policies
2. Implement user authentication
3. Use TLS certificates
4. Isolate network segments
5. Add firewall rules

## 🗺️ Roadmap

- [ ] Add more industrial protocols (BACnet, DNP3, EtherNet/IP)
- [ ] Implement OPC-UA security
- [ ] Add data buffering for network interruptions
- [ ] Support for OPC-UA methods and events
- [ ] Web-based configuration UI
- [ ] Kubernetes deployment manifests

## 📄 License

MIT License

## 📧 Contact

- GitHub: [@yourusername](https://github.com/yourusername)
- Blog: [yourblog.com](https://yourblog.com)

### This README written by Claude.ai
