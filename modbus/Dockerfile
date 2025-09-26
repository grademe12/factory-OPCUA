FROM python:3.11-slim

WORKDIR /app

RUN pip install pymodbus

COPY ./modbus_publisher.py .

CMD ["python", "-u", "modbus_publisher.py"]