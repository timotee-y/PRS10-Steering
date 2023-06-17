import tools.myserial as ms

def enquirevolt(ser):    
    try:
        # 发送指令
        command = b"SF?\r"
        ser.write(command)

        # 接收数据
        received_data = ms.receive_data(ser)

        # 将数据转换为字符串并打印
        received_string = received_data.decode('ascii')
        return received_string

    finally:
        # 关闭串口
        ser.close()

def expectvolt(curofst, freqdiff):
    freqdrift = int(freqdiff * 10 * 1e6 * 1e5)
    esf = int(curofst) - freqdrift
    cmd = ('SF ' + str(esf) + '\r').encode('utf-8')
    return esf, cmd