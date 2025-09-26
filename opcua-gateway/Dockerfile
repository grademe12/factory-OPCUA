FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && \
    pip install --no-cache-dir asyncua pymodbus && \
    apt-get remove -y gcc && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY opcua_gateway.py .

CMD ["python", "-u", "opcua_gateway.py"]