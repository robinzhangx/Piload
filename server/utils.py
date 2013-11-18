
def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0 and num > -1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')

def elapsed_time(seconds):
    str = ""
    s = abs(int(seconds))
    if s < 60:
        str = "%ds" % s
    elif s < 3600:
        str = "%dm" % int(s / 60)
    elif s < 86400:
        str = "%dh" % int(s / 3600)
    else:
        str = "%dd" % int(s / 86400)
    if seconds >= 0:
        return str
    else:
        return "-%s" % str