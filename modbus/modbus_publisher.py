# modbus_writer.py
import time
import os
import random
from pymodbus.client import ModbusTcpClient

class ModbusDataWriter:
    def __init__(self, host='localhost', port=502):
        """Modbus TCP 클라이언트 초기화"""
        self.client = ModbusTcpClient(host, port=port)
        
    def connect(self):
        """서버 연결"""
        return self.client.connect()
    
    def write_sensor_data(self):
        """센서 데이터 시뮬레이션 및 쓰기"""
        while True:
            try:
                # 가상 센서 데이터 생성
                temperature = random.uniform(20.0, 30.0)
                humidity = random.uniform(40.0, 60.0)
                pressure = random.uniform(1000.0, 1020.0)
                vibration = random.uniform(0.0, 10.0)
                production = random.randint(50, 150)
                
                # Float를 2개의 16비트 레지스터로 변환
                temp_registers = self._float_to_registers(temperature)
                humi_registers = self._float_to_registers(humidity)
                pres_registers = self._float_to_registers(pressure)
                vibr_registers = self._float_to_registers(vibration)
                
                # Holding Register에 쓰기 (주소 0부터)
                # 온도: 0-1, 습도: 2-3, 압력: 4-5, 진동: 6-7, 생산량: 8
                values = (
                    temp_registers + 
                    humi_registers + 
                    pres_registers + 
                    vibr_registers + 
                    [production]
                )
                
                # 레지스터에 쓰기 (FC 16: Write Multiple Registers)
                result = self.client.write_registers(0, values, device_id=1)
                
                if not result.isError():
                    print(f"✅ 데이터 쓰기 성공:")
                    print(f"  온도: {temperature:.2f}°C")
                    print(f"  습도: {humidity:.2f}%")
                    print(f"  압력: {pressure:.2f} hPa")
                    print(f"  진동: {vibration:.2f}")
                    print(f"  생산량: {production} units/hr")
                else:
                    print(f"❌ 쓰기 실패: {result}")
                
                time.sleep(5)  # 5초마다 업데이트
                
            except Exception as e:
                print(f"❌ 오류 발생: {e}")
                time.sleep(5)
    
    def _float_to_registers(self, value):
        """Float를 2개의 16비트 레지스터로 변환"""
        import struct
        # Float를 바이트로 변환
        bytes_val = struct.pack('>f', value)  # Big-endian
        # 2개의 16비트 정수로 변환
        registers = struct.unpack('>HH', bytes_val)
        return list(registers)
    
    def write_single_coil(self, address, value):
        """단일 코일 쓰기 (디지털 출력)"""
        result = self.client.write_coil(address, value, device_id=1)
        return not result.isError()
    
    def write_multiple_coils(self, address, values):
        """여러 코일 쓰기"""
        result = self.client.write_coils(address, values, device_id=1)
        return not result.isError()
    
    def close(self):
        """연결 종료"""
        self.client.close()

if __name__ == "__main__":
    # 환경변수에서 설정 가져오기
    host = os.getenv('MODBUS_HOST', 'localhost')
    port = int(os.getenv('MODBUS_PORT', 502))
    
    # Modbus 서버에 연결
    writer = ModbusDataWriter(host, port)
    
    if writer.connect():
        print(f"🔗 Modbus 서버 연결 성공: {host}:{port}")
        
        # 디지털 출력 예시
        writer.write_single_coil(0, True)   # 0번 코일 ON
        writer.write_single_coil(1, False)  # 1번 코일 OFF
        
        # 연속 데이터 쓰기 시작
        try:
            writer.write_sensor_data()
        except KeyboardInterrupt:
            print("\n👋 종료합니다...")
    else:
        print(f"❌ Modbus 서버 연결 실패: {host}:{port}")
    
    writer.close()