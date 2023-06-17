from ftplib import FTP
import os, time
import tools.myserial as ms
import tools.controlcmd as cc
import tools.date as mydate
from datetime import datetime
import numpy as np

def cv_difference(local_satnum, local_refsys, remote_satnum, remote_refsys, sys):
    # 找到本地组和远端组satnum列表中的相同元素
    common_satnums = set(local_satnum) & set(remote_satnum)

    # 存储相同元素对应的refsys列表的差值
    differences = {}

    # 计算差值并存储到字典中
    for satnum in common_satnums:
        local_index = local_satnum.index(satnum)
        remote_index = remote_satnum.index(satnum)
        diff = float(local_refsys[local_index]) - float(remote_refsys[remote_index])
        differences[satnum] = round((diff / 10), 1)
    
    listdir = []
    for value in differences.values():
        listdir.append(value)

    # 计算平均值及标准差
    if len(differences):
        average_diff = sum(differences.values()) / len(differences)
        std = np.std(listdir)
    else:
        return False

    # 打印结果
    # print("平均差值：", average_diff)
    if sys == 'BDS':
        print("Satellites in common view：", end = '')
        print(*[f'C{int(num):02d}' for num in common_satnums], sep = ',')
        print('Time diff on this CF: {:.2f}'.format(average_diff))
        print('std on this CF: {:.2f}'.format(std))
    elif sys == 'GPS':
        print("Satellites in common view：", end = '')
        print(*[f'G{int(num):02d}' for num in common_satnums], sep = ',')
        print('Time diff on this CF: {:.2f}'.format(average_diff))
        print('std on this CF: {:.2f}'.format(std))
    else:
        print('Unsupportted carrier frequency!!!')

    return average_diff, std

def ftp_download(remotefile):
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            ftp = FTP()
            port = 4567
            ftp.connect('ftp.timelinker.cn', port)
            ftp.login('user', 'user123')
            constate = True

            ftp.cwd('/REFSYS/TS31/')
            f = open('./rfileremote.txt', 'wb').write

            filename = 'RETR ' + remotefile
            # filename = 'RETR ' + 'RRZTS3159.953.57639'
            ftp.retrbinary(filename, f) # download from FTP to local txt
            ftp.quit()

            return constate

        except Exception as err:
            constate = False
            print('FTP connect ERROR !!!', err)
            
            # 限定重试次数与时间
            if attempt < max_retries - 1:
                print('Retrying...')
                time.sleep(retry_delay)
            else:
                print('Maximum retries exceeded.')

    return constate

def process_file(file_path):
    satnum = []
    mjd = []
    refsys = []

    with open(file_path, 'r') as file:
        lines = file.readlines()

        for i, line in enumerate(lines):
            if line.startswith('SAT'):
                # Check if there are at least two more lines available
                if i + 2 < len(lines):
                    for j in range (i + 2, len(lines)):
                        data = lines[j].split()
                        if len(data) >= 3:
                            first_col = data[0].strip()
                            second_col = data[1].strip()
                            third_col = data[2].strip()

                            # Extract the numeric part from the first column
                            num_part = ''.join(filter(str.isdigit, first_col))

                            # Store the extracted values in variables
                            satnum.append(num_part)
                            mjd.append(second_col)
                            refsys.append(third_col)

    return(satnum, mjd, refsys)

def get_timediff(filemjd):
    remote_header = ['RCZTS31', 'RCMTS31', 'RGZTS31', 'RGMTS31']
    time_diff = []
    std_deviation = []
    print('Waiting for remote files...')
    time.sleep(20) # 等待FTP上传 (通常FTP会在14-15s生成远端rfile)

    for i in range (0, 4):
        remote_file = remote_header[i] + filemjd # BeiDou L3B
        print('Downloading remote file:', remote_file)           

        # 打开最新文件
        file_path = os.path.join(folder_path, latest_file[i])
        local_satnum, local_mjd, local_refsys = process_file(file_path)

        if ftp_download(remote_file) == True:
            remote_satnum, remote_mjd, remote_refsys = process_file('./rfileremote.txt')
            for j in range (len(remote_satnum)):
                number = int(remote_satnum[j])
                if i < 2: # CGGTTS V2 北斗星号-100
                    number -= 100
                remote_satnum[j] = '{:02d}'.format(number)    

        else: # FTP下载失败
            return False
        
        # 共视时差
        if i < 2:
            print_flag = 'BDS'
        else:
            print_flag = 'GPS'
        
        temp_res = cv_difference(local_satnum, local_refsys, \
                                       remote_satnum, remote_refsys, print_flag)
        if temp_res:
            time_diff.append(temp_res[0])
            std_deviation.append(temp_res[1])   
        else: # 时差获取失败
            return False     

    deno = 0
    fusion_td = 0
    for k in range (0, 4):
        deno += 1 / (std_deviation[k] ** 2)

    for k in range (0, 4):
        fusion_td += time_diff[k] * ((1 / (std_deviation[k] ** 2)) / deno)

    return fusion_td

def get_steertime(strdt):
    cur_utc = time.strftime(strdt)
    cur_sec = mydate.calcCurTrackTime(cur_utc)
    cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cur_sec + 16 * 60))
    # fileName = 'RGZTL07' + mjd_time[0:2] + '.' + mjd_time[2:11]
    return cur_time   

# -------------------------------------------MAIN------------------------------------------ #
# 监听的文件夹路径
folder_path = '/home/tlab/TL01/DATA/rfile/'
port = "/dev/ttyUSB0" # pack to config yaml if possible
baudrate = 9600

# 初始化
last_modified_time = os.stat(folder_path).st_mtime
last_mjd = 0
last_timediff = 0
last_predicttimediff = 0
predict_timediff = 0
mod_phase = 0

print('*' * 15 + 'Waiting...' + '*' * 15)

while True:
    # 获取当前文件夹的最后修改时间
    current_modified_time = os.stat(folder_path).st_mtime    

    # 检查是否有新文件生成（最后修改时间发生变化）
    if current_modified_time != last_modified_time:
        time.sleep(1)
        last_modified_time = current_modified_time

        dt = datetime.fromtimestamp(current_modified_time)
        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S') # 文件生成年月日时分秒时刻

        steer_time = get_steertime(formatted_time)

        # 处理新文件
        file_list = os.listdir(folder_path)
        # 过滤出以"RCZ"开头且未处理过的文件
        new_files_CZ = [file_name for file_name in file_list if file_name.startswith('RCZ')]
        new_files_CM = [file_name for file_name in file_list if file_name.startswith('RCM')]
        new_files_GZ = [file_name for file_name in file_list if file_name.startswith('RGZ')]
        new_files_GM = [file_name for file_name in file_list if file_name.startswith('RGM')]

        # 对文件列表按照修改时间进行排序
        sorted_files_CZ = sorted(new_files_CZ, key=lambda x: os.stat(os.path.join(folder_path, x)).st_mtime)
        sorted_files_CM = sorted(new_files_CM, key=lambda x: os.stat(os.path.join(folder_path, x)).st_mtime)
        sorted_files_GZ = sorted(new_files_GZ, key=lambda x: os.stat(os.path.join(folder_path, x)).st_mtime)
        sorted_files_GM = sorted(new_files_GM, key=lambda x: os.stat(os.path.join(folder_path, x)).st_mtime)

        if sorted_files_CZ and sorted_files_CM and sorted_files_GZ and sorted_files_GM:
            # 获取最新的文件
            latest_file_CZ = sorted_files_CZ[-1] # 获取文件名
            latest_file_CM = sorted_files_CM[-1]
            latest_file_GZ = sorted_files_GZ[-1]
            latest_file_GM = sorted_files_GM[-1]
            latest_file = [latest_file_CZ, latest_file_CM, latest_file_GZ, latest_file_GM]

            filemjd = latest_file_CZ[-12:] # 获取MJD时刻

            if filemjd == last_mjd: # 排除错误判断
                continue

            # 判断三种轮（首轮、次轮与调整轮）
            if last_mjd == 0 and last_timediff == 0 and last_predicttimediff == 0:
                print('-' * 15 + 'Initial cycle.' + '-' * 15)
                time_diff = get_timediff(filemjd) # 获取时差
                if time_diff:                                     
                    print('Current status:', formatted_time, round(time_diff, 2))
                    print('Phase tuned:', mod_phase)
                else:
                    print('Failed to get time diff during this cycle!!!')
                    continue

            elif last_mjd and last_timediff and last_predicttimediff == 0:
                print('-' * 15 + 'Second cycle.' + '-' * 15)
                time_diff = get_timediff(filemjd) # 获取时差
                if time_diff:
                    mod_filemjd = float(filemjd.replace('.', '', 1)) # 格式xxxxx.xxxxx 
                    mod_lastmjd = float(last_mjd.replace('.', '', 1))
                    time_span = round((mod_filemjd - mod_lastmjd) * 60 * 24)

                    predict_timediff = \
                        float(time_diff) + (float(time_diff) - float(last_timediff)) \
                            / (time_span * 60 * 1e9) \
                            * (6.5 * 60 * 1e9 + 1 * 60 * 1e9)
                    # where time_span*60 represents for sample time, \
                    # 6.5 for half of the track time, 1 for waiting time of CGGTTS, \
                    # and 2 for waiting (canceled) \
                    # unit: ns

                    print('Time elapsed from last cycle: {} mins'.format(time_span))
                    print('Current status:', formatted_time, round(time_diff, 2))
                    print('Phase tuned:', mod_phase)
                    print('Precict timediff:', steer_time, round(predict_timediff, 2))

                    print('*' * 15 + 'Phase tuning...' + '*' * 15)

                    # Controling
                    while True:
                        cur_utc = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        if cur_utc == steer_time:                        
                            if round(predict_timediff) > 0:
                                value = 1e9 - round(predict_timediff)
                            elif round(predict_timediff) > 0:
                                value = 0 - round(predict_timediff)
                            elif predict_timediff == 0:
                                print('No phase tuning will be made.')

                            din = ('PP ' + str(int(value)) + '\r').encode('utf-8')                       
                            print('Ready to send cmd:', din)

                            # 发送指令 
                            ser = ms.openser(port, baudrate)
                            ser.write(din)

                            # 关闭串口
                            ser.close()
                            mod_phase = round(predict_timediff)
                            print('*' * 15 + 'Completed!!!' + '*' * 15)
                            break

                        time.sleep(1)                
                else:
                    print('Failed to get time diff during this cycle!!!')
                    continue        

            elif last_mjd and last_timediff and last_predicttimediff:
                print('-' * 15 + 'Adjusting cycle.' + '-' * 15)
                time_diff = get_timediff(filemjd) # 获取时差
                if time_diff:
                    mod_filemjd = float(filemjd.replace('.', '', 1)) # 格式xxxxx.xxxxx 
                    mod_lastmjd = float(last_mjd.replace('.', '', 1))
                    time_span = round((mod_filemjd - mod_lastmjd) * 60 * 24)

                    predict_timediff = \
                        float(time_diff) + (float(time_diff) - float(last_timediff)) \
                            / (time_span * 60 * 1e9) \
                            * (6.5 * 60 * 1e9 + 1 * 60 * 1e9)
                    # where time_span*60 represents for sample time, \
                    # 6.5 for half of the track time, 1 for waiting time of CGGTTS, \
                    # and 2 for waiting (canceled) \
                    # unit: ns

                    print('Time elapsed from last cycle: {} mins'.format(time_span))
                    print('Current status:', formatted_time, round(time_diff, 2))
                    print('Phase tuned:', mod_phase)
                    print('Precict timediff:', steer_time, round(predict_timediff, 2))

                    freqdiff = ((float(predict_timediff) - float(last_predicttimediff))) \
                        / (time_span * 60 * 1e9) 
                        
                    print('*' * 15 + 'Frequency tuning...' + '*' * 15)      

                    # Controling
                    while True:
                        cur_utc = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        if cur_utc == steer_time:
                            ser = ms.openser(port, baudrate)
                            curvolt = cc.enquirevolt(ser)
                            print("Current Clock Freq Offset =", curvolt, 'μHz')
                            (evolt, din) = cc.expectvolt(curvolt, freqdiff)                
                            print("Expected Clock Freq Offset =", evolt, 'μHz')                          

                            if evolt == int(curvolt):
                                print('No adjustment will be made during this cycle.')
                                break

                            # 发送指令 
                            print('Ready to send cmd:', din)
                            ser = ms.openser(port, baudrate)
                            ser.write(din)

                            # 关闭串口
                            ser.close()
                            print('*' * 15 + 'Completed!!!' + '*' * 15)
                            break

                        time.sleep(1)
                else:
                    print('Failed to get time diff during this cycle!!!')
                    continue 

            # 递推
            if filemjd:
                last_mjd = filemjd
                # plot_mjd.append(float(filemjd.replace('.', '', 1)))
            if time_diff:
                last_timediff = time_diff
                # plot_timediff.append(time_diff-mod_phase)
            if predict_timediff:
                last_predicttimediff = predict_timediff  

    # 休眠一段时间后再进行下一次轮询
    time.sleep(1)