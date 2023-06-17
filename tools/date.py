import math
import time
import datetime

def div(x, y):
    return int(round(x) / round(y))


def DF2DHMS(F):
    df = F

    day = math.floor(df)

    hour = math.floor((df - day) * 24)

    minute = math.floor((df - day - hour / 24) * 1440)

    sec = (df - day - hour / 24 - minute / 1440) * 86400

    return [day, hour, minute, int(sec)]


def strToTime(a):
    """
    时间字符串转时间戳
    :param a:时间字符串
    :return: 时间戳
    """
    timeArray = time.strptime(a, "%Y-%m-%d %H:%M:%S")
    timeStamp = int(time.mktime(timeArray))
    return timeStamp

def mjdTimeToHHMMSS(timestr):
    sec = int(int(timestr)*0.86400)
    hh = int(sec / 3600)
    mm = int((sec % 3600)/60)
    ss = int(sec % 60)

    hh_str = "{:0>2d}".format(hh)
    mm_str = "{:0>2d}".format(mm)
    ss_str = "{:0>2d}".format(ss)
    # print(str(hh),str(mm),str(ss))
    return hh_str+mm_str+ss_str

def mjdToTime(MJD,time):
    """
    儒略日转时间字符串
    :param MJD: 儒略日
    :param time: 时间字符串
    :return: 时间字符串格式
    """

    MJD = int(MJD)

    DJMIN = -68569.5

    DJMAX = 1e9

    DJ1 = 2400000.5

    DJ2 = MJD

    DJ = DJ1 + DJ2

    D1 = ''

    D2 = ''

    J = ''

    JD = ''

    if (DJ < DJMIN or DJ > DJMAX):

        J = -1

        print("无效的日期"+str(MJD))
    else:

        J = 0

        if (DJ1 >= DJ2):

            D1 = DJ1

            D2 = DJ2

        else:

            D1 = DJ2

            D2 = DJ1

        D2 = D2 - 0.5

        F1 = D1 % 1.0

        F2 = D2 % 1.0

        F = (F1 + F2) % 1.0

        if (F < 0): F = F + 1.0

        D = round(D1 - F1) + round(D2 - F2) + round(F1 + F2 - F)

        JD = round(D) + 1

        L = JD + 68569

        N = div(4 * L, 146097)

        L = L - div((146097 * N + 3), 4)

        I = div(4000 * (L + 1), 1461001)

        L = L - div(1461 * I, 4) + 31

        K = div(80 * L, 2447)

        ID = L - div(2447 * K, 80)
        if len(str(ID))<2:
            ID = "0"+str(ID)

        L = div(K, 11)

        IM = K + 2 - 12 * L
        if len(str(IM))<2:
            IM = "0"+str(IM)

        IY = 100 * (N - 49) + I + L

        FD = DF2DHMS(F)

        # print
        # MJD, '对应日期为', [IY, IM, int(ID), int(FD[1]), int(FD[2]), FD[3]]
        # print(str(IY)+"-"+str(IM)+"-"+str(ID)+" "+str(FD[1])+":"+str(FD[2])+":"+str(FD[3]))
        ss=str(IY)+"-"+str(IM)+"-"+str(ID)+" "+time[0:2]+":"+time[2:4]+":"+time[4:]

        return ss

# str1=mjdToTime("58122","085000")
# print(str1)


def stampToDate(timeStamp):
    """
    时间戳转日期字符串
    :param timeStamp: 1545004815 (s)
    :return: 2018-12-17 00:00:15
    """
    dateArray = datetime.datetime.utcfromtimestamp(timeStamp)
    otherStyleTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
    return otherStyleTime


# now_time = str(datetime.datetime.now()).split(".")[0]
# print(now_time)

def timeToMJD(mjd,time):
    """

    :param mjd: 58260
    :param time: 12:12:10
    :return: 58260.508449
    """

    mjd = int(mjd)
    d = int(time[0:2])*3600
    s = int(time[2:4])*60
    m = int(time[4:])
    # num = round(mjd+(d+s+m)/86400,6)
    num = round(mjd+(d+s+m)/86400,5)
    # print("aaa",num)
    # print("{:x<12f}".format(num))
    num_str = "{:x<12f}".format(num)
    # print("num_str", num_str)
    # ret_str = num_str[0:2] + '.' + num_str[2:11]
    ret_str = num_str[0:11]
    # print("aaa",ret_str)
    return ret_str
    # return "{:x<12f}".format(num)
# aa = timeToMJD("58260","121210")
# print(aa)


def timestrToMjd(datestr):
    """
    时间字符串转mjd

    :param datestr: 2018-01-05 08:50:00
    :return: 58123
    """
    string = datestr.split(" ")[0]
    y = int(string.split("-")[0])
    m = int(string.split("-")[1])
    d = int(string.split("-")[2])

    # jd = d - 32075 + 1461 * (y + 4800 + (m - 14) / 12) / 4 + 367 * (m - 2 - (m - 14) / 12 * 12) / 12 - 3 * (
    # (y + 4900 + (m - 14) / 12) / 100) / 4
    #
    # mjdStr = str(jd-2400000.5)
    # x = mjdStr.index(".")
    # if x == -1:
    #     return int(mjdStr)
    # else:
    #     mjdStr = mjdStr[0:x]
    #     return int(mjdStr)

    return ce2jd(y,m,d)

    ## 2022.1.31,2022.2.1 2022.4.6都不对



def gyjn(year):
    if year > 1:
        ce = "公元" + str(year)
    elif year == 1:
        ce = "公元元"
    elif year <= 0:
        year -= 1
        ce = "公元前" + str(-year)
    return ce

def ce2jd(Year, Month, D):
    if Month in [1, 2]:
        M = Month + 12
        Y = Year - 1
    else:
        Y = Year
        M = Month
    B = 0
    if Y > 1582 or (Y == 1582 and M > 10) or (Y == 1582 and M == 10 and D >= 15):
        B = 2 - int(Y / 100) + int(Y / 400)  # 公元1582年10月15日以后每400年减少3闰
    JD = math.floor(365.25 * (Y + 4716)) + int(30.6 * (M + 1)) + D + B - 1524.5
    # JD = math.floor(365.25*(Y+4712))+int(30.6*(M+1))+D+B-63.5
    # print("{}年{}月{}日的儒略日为：{:.5f}".format(gyjn(Year), Month, D, JD))
    if Y > 1858 or (Y == 1858 and M > 11) or (Y == 1858 and M == 11 and D >= 17):
        MJD = int(JD - 2400000.5)
        # print("简化儒略日为：{}".format(MJD))
    return MJD

#a = timestrToMjd("2018-01-05 08:50:00")

#print(a)

#daytorulueri("58023","234200")
#print(date("58023","010200"))

def getCurrentMJDandSTTime():
    current_datetime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))
    current_time = time.strftime('%H%M%S', time.gmtime(time.time()))
    current_mjd = timestrToMjd(current_datetime)
    current_mjd_sttime = timeToMJD(current_mjd,current_time)

    return current_mjd_sttime

def getMJDandSTTime(timestr):
    current_datetime = time.strftime(timestr)
    # print(timestr[11:19])
    mytime = timestr[11:13]+timestr[14:16]+timestr[17:19]
    # print("ttt",timestr,timestr[14:16])
    current_time = time.strftime(mytime)
    current_mjd = timestrToMjd(current_datetime)
    current_mjd_sttime = timeToMJD(current_mjd,current_time)

    return current_mjd_sttime

def composeTime(time1):
    time2 = datetime.datetime.strptime(time1, "%Y-%m-%d %H:%M:%S")
    time3 = time.mktime(time2.timetuple())
    time4 = int(time3)
    return time4

def calcNextTrackTime(dtstr):
    # baseTime = datetime.datetime(1997,10,1,0,2,0)
    # cur_utc = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))
    cur_utc = dtstr
    base_sec = composeTime("1997-10-1 00:02:00")
    cur_sec = composeTime(cur_utc)
    totalOutSec = cur_sec - base_sec
    # 89*16 + 12 = 1436
    outSec1 = totalOutSec %(1436 * 60)
    wait_sec = 0
    duan = outSec1 / (16*60)
    outSec2 = outSec1 % (16*60)

    if(duan < 88):
        if(outSec2 == 0):
            wait_sec = 0
        else:
            wait_sec = 16*60 - outSec2
    elif(duan == 88):
        if(outSec2 == 0):
            wait_sec = 0
        else: #从28分钟中剔除
            wait_sec = 28*16 - outSec2
    elif(duan == 89): #最后12分钟，剔除
        wait_sec = 12*16 - outSec2

    next_time = cur_sec + wait_sec
    return next_time

## 当前跟踪时间
def calcCurTrackTime(dtstr):
    # baseTime = datetime.datetime(1997,10,1,0,2,0)
    # cur_utc = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))
    cur_utc = dtstr
    base_sec = composeTime("1997-10-1 00:02:00")
    cur_sec = composeTime(cur_utc)
    totalOutSec = cur_sec - base_sec
    # 89*16 + 12 = 1436
    outSec1 = totalOutSec %(1436 * 60)
    wait_sec = 0
    duan = outSec1 / (16*60)
    outSec2 = outSec1 % (16*60)

    if(duan < 88):
        if(outSec2 == 0):
            wait_sec = 0
        else:
            wait_sec = outSec2
    elif(duan == 88):
        if(outSec2 == 0):
            wait_sec = 0
        else: #从28分钟中剔除
            wait_sec = outSec2
    elif(duan == 89): #最后12分钟，补偿上
        wait_sec = 12*16 + outSec2

    cur_time = cur_sec - wait_sec
    return cur_time

# print(timestrToMjd("2017-03-26 06:02:00"))
# print(mjdToTime("57838", "001424"))
# print(timeToMJD("58123","001424"))
# # gmtime utc, localtime
# print("当前UTC时间:", time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time())))
# # 59.676.45213
# print(getCurrentMJDandSTTime())
# cur_utc = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))
# # cur_utc = "2022-04-06 06:08:00"
# cur_utc = "2022-04-06 08:08:00"
# next_sec = calcNextTrackTime(cur_utc)
# cur_sec = calcCurTrackTime(cur_utc)
# next_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_sec))
# cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cur_sec))
# print("当前跟踪时间:", cur_time)
# print("当前文件名:", getMJDandSTTime(cur_time))
# print("下一个跟踪时间:", next_time)
# print("下一个文件名:", getMJDandSTTime(next_time))
# print(mjdTimeToHHMMSS(30625))


