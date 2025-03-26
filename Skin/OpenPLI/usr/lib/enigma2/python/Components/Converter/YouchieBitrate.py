#######################################################
#                                                     #
#    Youchie-PLI-FHD Bitrate Converter for Enigma2    #
#                                                     #
#######################################################

from __future__ import absolute_import
from enigma import (
    eConsoleAppContainer,
    eTimer,
    iServiceInformation,
)
from Components.Console import Console
from Components.Converter.Converter import Converter
from Components.Element import cached
import six
from datetime import datetime
from os import path
imageType = None
DBG = False
append2file = False


def YPFDEBUG(myText=None, Append=True, myDEBUG='/tmp/YouchieComponents.log'):
    global append2file
    if myDEBUG is None or myText is None:
        return
    try:
        if append2file is False or Append is False:
            append2file = True
            mode = 'w'
        else:
            mode = 'a'
        with open(myDEBUG, mode) as f:
            f.write('%s\t%s\n' % (str(datetime.now()), myText))
        if path.getsize(myDEBUG) > 100000:
            with open(myDEBUG, 'r+') as f:
                lines = f.readlines()
                f.seek(0)
                f.writelines(lines[10:])
                f.truncate()
    except Exception as e:
        with open(myDEBUG, 'a') as f:
            f.write('Exception: %s\n' % str(e))
    return


def isImageType(imgName=''):
    global imageType
    if imageType is None:
        if path.exists('/etc/opkg/all-feed.conf'):
            with open('/etc/opkg/all-feed.conf', 'r') as file:
                fileContent = file.read()
                file.close()
                fileContent = fileContent.lower()
                if fileContent.find('VTi') > -1:
                    imageType = 'vti'
                elif fileContent.find('code.vuplus.com') > -1:
                    imageType = 'vuplus'
                elif fileContent.find('openpli-7') > -1:
                    imageType = 'openpli7'
                elif fileContent.find('openatv') > -1:
                    imageType = 'openatv'
                    if fileContent.find('/5.3/') > -1:
                        imageType += '5.3'
    if imageType is None:
        if path.exists('/usr/lib/enigma2/python/Plugins/SystemPlugins/VTIPanel/'):
            imageType = 'vti'
        elif path.exists('/usr/lib/enigma2/python/Plugins/Extensions/Infopanel/'):
            imageType = 'openatv'
        elif path.exists('/usr/lib/enigma2/python/Blackhole'):
            imageType = 'blackhole'
        elif path.exists('/etc/init.d/start_pkt.sh'):
            imageType = 'pkt'
        else:
            imageType = 'unknown'
    if imgName.lower() == imageType.lower():
        return True
    else:
        return False


class YouchieBitrate(Converter, object):

    def __init__(self, type):
        Converter.__init__(self, type)
        self.clearValues()
        self.isRunning = False
        self.isSuspended = False
        self.myConsole = Console()
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.appClosed)
        self.container.dataAvail.append(self.dataAvail)
        self.StartTimer = eTimer()
        self.StartTimer.callback.append(self.start)
        self.StartTimer.start(100, True)
        self.runTimer = eTimer()
        self.runTimer.callback.append(self.runBitrate)
        self.myConsole.ePopen('chmod 755 /usr/bin/bitrate')

    @cached
    def getText(self):
        if DBG:
            YPFDEBUG("[YouchieBitrate:getText] vcur %s" % self.vcur)
        if self.vcur > 0:
            return '%d Kb/s' % self.vcur
        else:
            return ''

    text = property(getText)

    def doSuspend(self, suspended):
        if DBG:
            YPFDEBUG("[YouchieBitrate:suspended] >>> self.isSuspended=%s, suspended=%s" % (self.isSuspended, suspended))
        if suspended == 0:
            self.isSuspended = False
            self.StartTimer.start(100, True)
        else:
            self.StartTimer.stop()
            self.isSuspended = True
            self.myConsole.ePopen('killall -9 bitrate', self.clearValues)

    def start(self):
        if self.isRunning is False:
            if self.source.service:
                if DBG:
                    YPFDEBUG("[YouchieBitrate:start] initiate runTimer")
                self.isRunning = True
                self.runTimer.start(100, True)
            else:
                if DBG:
                    YPFDEBUG("[YouchieBitrate:start] wait 100ms for self.source.service")
                self.StartTimer.start(100, True)
        else:
            if DBG:
                YPFDEBUG("[YouchieBitrate:start] runBitrate in progress, nothing to do")

    def runBitrate(self):
        if DBG:
            YPFDEBUG("[YouchieBitrate:runBitrate] >>>")
        if isImageType('vti'):
            demux = 2
        else:
            adapter = 0
            demux = 0
        try:
            stream = self.source.service.stream()
            if stream:
                if DBG:
                    YPFDEBUG("[YouchieBitrate:runBitrate] Collecting stream data...")
                streamdata = stream.getStreamingData()
                if streamdata:
                    if 'demux' in streamdata:
                        demux = streamdata['demux']
                        if demux < 0:
                            demux = 0
                    if 'adapter' in streamdata:
                        adapter = streamdata["adapter"]
                        if adapter < 0:
                            adapter = 0
        except Exception as e:
            if DBG:
                YPFDEBUG("[YouchieBitrate:runBitrate] Exception collecting stream data: %s" % str(e))
        try:
            info = self.source.service.info()
            vpid = info.getInfo(iServiceInformation.sVideoPID)
            apid = info.getInfo(iServiceInformation.sAudioPID)
        except Exception as e:
            if DBG:
                YPFDEBUG("[YouchieBitrate:runBitrate] Exception collecting service info: %s" % str(e))
            return  # bitrate cannot be run without vpid and apid
        if vpid >= 0 and apid >= 0:
            if isImageType('vti'):
                cmd = 'killall -9 bitrate > /dev/null 2>&1; nice bitrate %i %i %i' % (demux, vpid, vpid)
            else:
                cmd = 'killall -9 bitrate > /dev/null 2>&1;nice bitrate %i %i %i %i' % (adapter, demux, vpid, vpid)
            if DBG:
                YPFDEBUG('[YouchieBitrate:runBitrate] starting "%s"' % cmd)
            self.container.execute(cmd)

    def clearValues(self, *args):  # invoked by appClosed & kill from suspend
        if DBG:
            YPFDEBUG("[YouchieBitrate:clearValues] >>>")
        self.isRunning = False
        self.vmin = self.vmax = self.vavg = self.vcur = 0
        self.amin = self.amax = self.aavg = self.acur = 0
        self.remainingdata = ''
        self.datalines = []
        Converter.changed(self, (self.CHANGED_POLL,))

    def appClosed(self, retval):
        if DBG:
            YPFDEBUG("[YouchieBitrate:appClosed] >>> retval=%s, isSuspended=%s" % (retval, self.isSuspended))
        if self.isSuspended is True:
            self.clearValues()
        else:
            self.runTimer.start(100, True)

    def dataAvail(self, conStr):
        if DBG:
            YPFDEBUG("[YouchieBitrate:dataAvail] >>> conStr '%s'\n\tself.remainingdata='%s'" % (conStr, self.remainingdata))
        if six.PY2:
            conStr = self.remainingdata + str(conStr)
        else:
            conStr = self.remainingdata + str(conStr, 'utf-8', 'ignore')
        newlines = conStr.split('\n')
        if len(newlines[-1]):  # checks if last line contains any data, it will be used next time if so
            self.remainingdata = newlines[-1]
            newlines = newlines[0:-1]
        else:
            self.remainingdata = ''
        for line in newlines:
            if len(line):
                self.datalines.append(line)

        if len(self.datalines) >= 2:
            try:
                self.vmin, self.vmax, self.vavg, self.vcur = [int(x) for x in self.datalines[0].split(' ')]
                self.amin, self.amax, self.aavg, self.acur = [int(x) for x in self.datalines[1].split(' ')]
            except Exception:
                pass
            self.datalines = []
            Converter.changed(self, (self.CHANGED_POLL,))
