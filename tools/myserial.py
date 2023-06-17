import serial
import serial.tools.list_ports
import binascii, time

def openser(port, baudrate): # open serial
    ser = serial.Serial(port, baudrate)
    if ser.isOpen():
        print("Connecting to serial:", ser.name)
    else:
        print("Serial Connecting ERROR !!!")
    return ser

def serclose(ser): # close serial
    ser.close()
    if ser.isOpen():
        print("Disconnecting serial failed !!!")
    else:
        print("Serial disconnected.")
        print()

def receive_data(serial_port):
    data = b""
    while True:
        # 从串口读取一个字节
        byte = serial_port.read()

        # 如果读取到回车符则停止接收
        if byte == b'\r':
            break

        # 将字节添加到数据中
        data += byte

    return data