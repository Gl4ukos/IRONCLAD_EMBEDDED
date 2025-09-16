import serial
import time


class MotorDriver:
    def __init__(self, max_expected_speed):
        self.DEV_ADDR = 0x32
        self.DUTY_REG_ADDR = 0x0006
        self.FREQ_REG_ADDR = 0x0007
        self.PWM_EN_REG_ADDR = 0x0008

        self.PWM_freq_factor = 4

        self.max_expected_speed = max_expected_speed
        self.inv_speed_incremental = 1/25
        self.speed_values = [
            0,
            25,
            50,
            75,
            100,
            125,
            150,
            175,
            200,
            225,
            250
        ]

        self.ser = serial.Serial("/dev/ttyAMA0", 9600, timeout=1)
        print("->>> SETTING UP UART CONNECTION...")
        time.sleep(1)
        
        self.write_register( self.FREQ_REG_ADDR, self.PWM_freq_factor) #setting PWM frequency
        print("->>> SETTING UP DRIVER REGISTERS...")

        time.sleep(0.5)
        self.write_register( self.DUTY_REG_ADDR, 0) # setting Duty to 0 (speed)
        time.sleep(0.5)
        self.write_register( self.PWM_EN_REG_ADDR, 1) #enabling engine
        print("->>> POWERING UP...")
        time.sleep(0.5)
        print("->>> ENGINE ENABLED\n******************\n")
        time.sleep(1)

    def calc_crc(self,data: bytes) -> bytes:
        crc = 0xFFFF
        for pos in data:
            crc ^= pos
            for _ in range(8):
                if (crc & 0x0001) != 0:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        # The Arduino code (from the documentation website) swapped the bytes here
        crc = ((crc & 0x00FF) << 8) | ((crc & 0xFF00) >> 8)
        return crc.to_bytes(2, 'big')

    def write_register(self, reg_addr: int, value: int):
        frame = bytearray()
        frame.append(self.DEV_ADDR)
        frame.append(0x06)  # Write Single Register
        frame.extend(reg_addr.to_bytes(2, 'big'))
        frame.extend(value.to_bytes(2, 'big'))
        crc = self.calc_crc(frame)
        frame.extend(crc)
        self.ser.write(frame)

    # assuming min speed: 0.0
    def normalize_speed(self, val):
        clipped = max(min(val,self.max_expected_speed),0.0)
        return (clipped * self.speed_values[-1]) / self.max_expected_speed
        
    def send_speed(self, speed:float):
        normalized = self.normalize_speed(speed)
        print("sent speed: ", speed, "-> ",normalized)
        self.write_register(self.DUTY_REG_ADDR, round(normalized))


    def send_speed_by_index(self, speed_index:int):
        #print("sent speed: ", self.speed_values[speed_index])
        self.write_register(self.DUTY_REG_ADDR, self.speed_values[speed_index])
    
    def shutdown_engine(self):
        self.write_register(self.DUTY_REG_ADDR, 0) #zero speed
        time.sleep(1)
        print("->>> POWERING DOWN...")
        self.write_register( self.PWM_EN_REG_ADDR, 0) #disable engine
        print("->>> ENGINE OFF\n**************\n")

    def terminate_serial_connection(self):
        time.sleep(1)
        self.ser.close()
        print("->>> CONNECTION TERMINATED")

if __name__ == "__main__":
    driver = MotorDriver(30)

    time.sleep(1)

    driver.send_speed(5)

    time.sleep(3)

    driver.send_speed(8)

    time.sleep(3)

    driver.send_speed(15)

    time.sleep(2)

    driver.send_speed(0)

    driver.shutdown_engine()
    driver.terminate_serial_connection()
