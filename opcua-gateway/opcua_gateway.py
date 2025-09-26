# opcua_gateway.py
import asyncio
import os
import logging
from datetime import datetime
from asyncua import Server, ua
from pymodbus.client import ModbusTcpClient

logging.basicConfig(level=logging.INFO)
logging.getLogger("asyncua").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

class OPCUAModbusGateway:
    def __init__(self):
        self.modbus_host = os.getenv('MODBUS_HOST', 'modbus-device')
        self.modbus_port = int(os.getenv('MODBUS_PORT', 5020))
        self.opcua_port = int(os.getenv('OPCUA_PORT', 4840))
        
        self.modbus_client = None
        self.opcua_server = None
        self.nodes = {}
        
    async def init_opcua_server(self):
        """OPC-UA 서버 초기화"""
        self.opcua_server = Server()
        await self.opcua_server.init()
        
        self.opcua_server.set_endpoint(f"opc.tcp://0.0.0.0:{self.opcua_port}/pearl-factory/server")
        self.opcua_server.set_server_name("Pearl Factory OPC-UA Server")
        
        # 네임스페이스 등록
        uri = "http://pearl-factory.opcua"
        idx = await self.opcua_server.register_namespace(uri)
        
        # 객체 노드 생성
        objects = self.opcua_server.get_objects_node()
        plc_node = await objects.add_object(idx, "ModbusPLC")
        
        # 센서 데이터 노드 생성
        self.nodes['temperature'] = await plc_node.add_variable(
            idx, "Temperature", 0.0, ua.VariantType.Double)
        print(f"Temperature NodeID: {self.nodes['temperature'].nodeid}")
        self.nodes['humidity'] = await plc_node.add_variable(
            idx, "Humidity", 0.0, ua.VariantType.Double)
        print(f"Humidity NodeID: {self.nodes['humidity'].nodeid}")
        self.nodes['pressure'] = await plc_node.add_variable(
            idx, "Pressure", 0.0, ua.VariantType.Double)
        self.nodes['vibration'] = await plc_node.add_variable(
            idx, "Vibration", 0.0, ua.VariantType.Double)
        self.nodes['production'] = await plc_node.add_variable(
            idx, "Production", 0, ua.VariantType.Int64)
        
        # 노드 쓰기 가능 설정
        for node in self.nodes.values():
            await node.set_writable()
            
        logger.info(f"OPC-UA 서버 초기화 완료: port {self.opcua_port}")
        
    def init_modbus_client(self):
        """Modbus 클라이언트 초기화"""
        self.modbus_client = ModbusTcpClient(self.modbus_host, port=self.modbus_port)
        if self.modbus_client.connect():
            logger.info(f"Modbus 연결 성공: {self.modbus_host}:{self.modbus_port}")
            return True
        else:
            logger.error(f"Modbus 연결 실패: {self.modbus_host}:{self.modbus_port}")
            return False
    
    def registers_to_float(self, registers, index):
        """2개의 16비트 레지스터를 float로 변환"""
        import struct
        if index + 1 < len(registers):
            # Big-endian으로 결합
            bytes_val = struct.pack('>HH', registers[index], registers[index+1])
            return struct.unpack('>f', bytes_val)[0]
        return 0.0
    
    async def poll_modbus_data(self):
        """Modbus에서 데이터 읽어서 OPC-UA 노드 업데이트"""
        while True:
            try:
                # Holding Register 읽기 (0-8번)
                result = self.modbus_client.read_holding_registers(0, count=9)
                
                if not result.isError():
                    registers = result.registers
                    
                    # Float 값들 파싱
                    temperature = self.registers_to_float(registers, 0)
                    humidity = self.registers_to_float(registers, 2)
                    pressure = self.registers_to_float(registers, 4)
                    vibration = self.registers_to_float(registers, 6)
                    production = registers[8] if len(registers) > 8 else 0
                    
                    # OPC-UA 노드 업데이트
                    await self.nodes['temperature'].write_value(temperature)
                    await self.nodes['humidity'].write_value(humidity)
                    await self.nodes['pressure'].write_value(pressure)
                    await self.nodes['vibration'].write_value(vibration)
                    await self.nodes['production'].write_value(production)
                    
                    logger.info(f"데이터 업데이트: T={temperature:.2f}°C, H={humidity:.2f}%, P={pressure:.2f}hPa")
                else:
                    logger.error(f"Modbus 읽기 오류: {result}")
                    
            except Exception as e:
                logger.error(f"폴링 오류: {e}")
                
            await asyncio.sleep(5)  # 5초마다 폴링
    
    async def run(self):
        """메인 실행"""
        # OPC-UA 서버 시작
        await self.init_opcua_server()
        
        # Modbus 클라이언트 연결
        while not self.init_modbus_client():
            logger.info("Modbus 재연결 시도 중...")
            await asyncio.sleep(5)
        
        async with self.opcua_server:
            logger.info("OPC-UA 서버 시작됨")
            
            # Modbus 폴링 태스크 시작
            polling_task = asyncio.create_task(self.poll_modbus_data())
            
            try:
                await asyncio.Future()  # 무한 대기
            except KeyboardInterrupt:
                polling_task.cancel()
                logger.info("서버 종료 중...")

if __name__ == "__main__":
    gateway = OPCUAModbusGateway()
    asyncio.run(gateway.run())