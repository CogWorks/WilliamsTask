import colorsys, datetime, time, platform

def hsv_to_rgb(h, s, v):
    return tuple(map(lambda x: int(x * 255), list(colorsys.hsv_to_rgb(h / 360., s / 100., v / 100.))))

def getDateTimeStamp():
    d = datetime.datetime.now().timetuple()
    return "%d-%d-%d_%d-%d-%d" % (d[0], d[1], d[2], d[3], d[4], d[5])

get_time = time.time
if platform.system() == 'Windows':
    get_time = time.clock