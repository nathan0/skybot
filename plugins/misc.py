import socket
import subprocess, commands
import time
import os

from util import hook, http

socket.setdefaulttimeout(10)  # global setting


def get_version():
    try:
        stdout = subprocess.check_output(['git', 'log', '--format=%h'])
    except:
        revnumber = 0
        shorthash = '????'
    else:
        revs = stdout.splitlines()
        revnumber = len(revs)
        shorthash = revs[0]

    http.ua_skybot = 'Skybot/r%d %s (http://github.com/nathan0/skybot)' \
        % (revnumber, shorthash)

    return shorthash, revnumber


# autorejoin channels
@hook.event('KICK')
def rejoin(paraml, conn=None):
    if paraml[1] == conn.nick:
        if paraml[0].lower() in conn.conf.get("channels", []):
            time.sleep(3)
            conn.join(paraml[0])


# join channels when invited
@hook.event('INVITE')
def invite(paraml, conn=None, bot=None, input=None):
    if input.nick+"@"+input.host in conn.conf.get("admins",[]):
        conn.join(paraml[-1])

@hook.event('004')
def onjoin(paraml, conn=None):
    # identify to services
    nickserv_password = conn.conf.get('nickserv_password', '')
    nickserv_name = conn.conf.get('nickserv_name', 'nickserv')
    nickserv_command = conn.conf.get('nickserv_command', 'IDENTIFY %s')
    if nickserv_password:
        conn.msg(nickserv_name, nickserv_command % nickserv_password)
        time.sleep(1)

    # set mode on self
    mode = conn.conf.get('mode')
    if mode:
        conn.cmd('MODE', [conn.nick, mode])

    # join channels
    for channel in conn.conf.get("channels", []):
        conn.join(channel)
        time.sleep(1)  # don't flood JOINs

    # set user-agent
    ident, rev = get_version()


@hook.regex(r'^\x01VERSION\x01$')
def version(inp, notice=None):
    ident, rev = get_version()
    notice('\x01VERSION skybot %s r%d - http://github.com/nathan0/'
           'skybot/\x01' % (ident, rev))

@hook.command("gi",autohelp=False)
@hook.command(autohelp=False)
def getinfo(inp, say=None, input=None):
    "getinfo -- returns PID, Threads and Virtual Memory"
    PID = os.getpid()
    ident, rev = get_version()
    threads = commands.getoutput("cat /proc/%s/status | grep Threads | awk '{print $2}'"%PID)
    memory = int(commands.getoutput("cat /proc/%s/status | grep VmRSS | awk '{print $2}'"%PID))/1000
    say("Version: %s-%s; PID: %s; Host: %s; Threads: %s; Virtual Memory: %s MB"%(ident,rev,os.getpid(),socket.gethostname(),threads,memory))

@hook.command(autohelp=False)
def source(inp):
    ident, rev = get_version()
    return 'skybot %s r%d - http://github.com/nathan0/skybot/' % (ident, rev)

@hook.command
def metrictime(inp):
    "metrictime <hours(0-23)>:<minutes(0-59)>:<seconds(0-59)> -- convert 24-hour time into metric time"
    if inp.count(":") == 2:
        hours,minutes,seconds = inp.split(":")
        try:
            hours = int(hours)
            minutes = int(minutes)
            seconds = int(seconds)
        except:
            return "That's not a time"
        if hours < 0 or hours >= 24: return "Hours must be between 0 and 23"
        if minutes < 0 or minutes >= 60: return "Minutes must be between 0 and 59"
        if seconds < 0 or seconds >= 60: return "Seconds must be between 0 and 59"
        daysecs = 3600*hours + 60*minutes + seconds
        metricsecs = daysecs * 100000 / 86400
        metrichours = math.floor(metricsecs / 10000)
        metricsecs = metricsecs - 10000 * metrichours
        metricminutes = math.floor(metricsecs / 100)
        metricsecs = math.floor(metricsecs - 100 * metricminutes)
        if metrichours <= 9: metrichours = "0"+str(metrichours)
        if metricminutes <= 9: metricminutes = "0"+str(metricminutes)
        if metricsecs <= 9: metricsecs = "0"+str(metricsecs)
        metrichours = str(metrichours).split(".")[0]
        metricminutes = str(metricminutes).split(".")[0]
        metricsecs = str(metricsecs).split(".")[0]
        metric = metrichours+":"+metricminutes+":"+metricsecs
        return "%s in metric: %s"%(inp,metric)
    else:
        return "Usage: metrictime <hours(0-23)>:<minutes(0-59)>:<seconds(0-59)>"

@hook.command("uptime",autohelp=False)
def showuptime(inp):
    "uptime -- shows how long I have been connected for"
    f = open("uptime","r")
    uptime = f.read()
    f.close()
    uptime = timesince.timesince(float(uptime))
    return "I have been online for %s"%uptime
