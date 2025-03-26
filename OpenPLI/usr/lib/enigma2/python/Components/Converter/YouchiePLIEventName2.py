#  Youchie-PLI-FHD Converter for Enigma2

from Components.Converter.Converter import Converter
from Components.Element import cached
from enigma import eEPGCache, eServiceReference
from time import localtime, time, mktime, strftime
from datetime import datetime

class YouchiePLIEventName2(Converter, object):
    NAME = 0
    NAME_TWEAKED = 1
    SHORT_DESCRIPTION = 2
    EXTENDED_DESCRIPTION = 3
    FULL_DESCRIPTION = 4
    ID = 5
    NEXT_NAME = 6
    NEXT_DESCRIPTION = 7
    NEXT_NAMEWT = 8
    NEXT_NAME_NEXT = 9
    NEXT_NAME_NEXTWT = 10
    NEXT_EVENT_LIST = 11
    NEXT_EVENT_LISTWT = 12
    NEXT_EVENT_LIST2 = 13
    NEXT_EVENT_LISTWT2 = 14
    NEXT_TIME_DURATION = 15
    PRIME_TIME_NO_DURATION = 16
    PRIME_TIME_ONLY_DURATION = 17
    PRIME_TIME_WITH_DURATION = 18

    def __init__(self, type):
        Converter.__init__(self, type)
        self.epgcache = eEPGCache.getInstance()
        if type == 'NameTweaked':
            self.type = self.NAME_TWEAKED
        elif type == 'Description' or type == 'Short':
            self.type = self.SHORT_DESCRIPTION
        elif type == 'ExtendedDescription':
            self.type = self.EXTENDED_DESCRIPTION
        elif type == 'FullDescription' or type == 'ShortOrExtendedDescription':
            self.type = self.FULL_DESCRIPTION
        elif type == 'ID':
            self.type = self.ID
        elif type == 'NextName':
            self.type = self.NEXT_NAME
        elif type == 'NextNameNext':
            self.type = self.NEXT_NAME_NEXT
        elif type == 'NextNameNextWithOutTime':
            self.type = self.NEXT_NAME_NEXTWT
        elif type == 'NextNameWithOutTime':
            self.type = self.NEXT_NAMEWT
        elif type == 'NextDescription' or type == 'NextEvent':
            self.type = self.NEXT_DESCRIPTION
        elif type == 'NextEventList':
            self.type = self.NEXT_EVENT_LIST
        elif type == 'NextEventListWithOutTime':
            self.type = self.NEXT_EVENT_LISTWT
        elif type == 'NextEventList2':
            self.type = self.NEXT_EVENT_LIST2
        elif type == 'NextEventListWithOutTime2':
            self.type = self.NEXT_EVENT_LISTWT2
        elif type == 'NextTimeDuration':
            self.type = self.NEXT_TIME_DURATION
        elif type == 'PrimeTimeNoDuration':
            self.type = self.PRIME_TIME_NO_DURATION
        elif type == 'PrimeTimeOnlyDuration':
            self.type = self.PRIME_TIME_ONLY_DURATION
        elif type == 'PrimeTimeWithDuration':
            self.type = self.PRIME_TIME_WITH_DURATION
        else:
            self.type = self.NAME

    @cached
    def getText(self):
        event = self.source.event
        if event is None:
            return ''
        elif self.type is self.NAME:
            return event.getEventName()
        elif self.type is self.NAME_TWEAKED:
            description = '%s %s' % (event.getEventName().strip(), event.getShortDescription().strip())
            return description.replace('DOLBY, 16:9', '').replace('(', '').replace(')', '').replace('|', '').replace('0+', '').replace('16+', '').replace('6+', '').replace('12+', '').replace('18+', '')
        elif self.type is self.SHORT_DESCRIPTION:
            return event.getShortDescription()
        elif self.type is self.EXTENDED_DESCRIPTION:
            text = event.getShortDescription()
            if text and text[-1] is not '\n' and text[-1] is not ' ':
                text += ' '
            text = text + event.getExtendedDescription() or event.getEventName()
            if 'EPG-SAT.DE' in text:
                return ''
            return text
        elif self.type is self.FULL_DESCRIPTION:
            description = event.getShortDescription()
            extended = event.getExtendedDescription()
            if description and extended:
                description += '\n'
            return description + extended
        elif self.type is self.ID:
            return str(event.getEventId())
        elif self.type is self.PRIME_TIME_NO_DURATION or self.type is self.PRIME_TIME_ONLY_DURATION or self.type is self.PRIME_TIME_WITH_DURATION:
            reference = self.source.service
            current_event = self.source.getCurrentEvent()
            if current_event:
                now = localtime(time())
                dt = datetime(now.tm_year, now.tm_mon, now.tm_mday, 20, 15)
                self.epgcache.startTimeQuery(eServiceReference(reference.toString()), int(mktime(dt.timetuple())))
                next = self.epgcache.getNextTimeEntry()
                if next and next.getBeginTime() <= int(mktime(dt.timetuple())):
                    begin = strftime('%H:%M', localtime(next.getBeginTime()))
                    end = strftime('%H:%M', localtime(next.getBeginTime() + next.getDuration()))
                    title = next.getEventName()
                    duration = _('%d min') % (next.getDuration() / 60)
                    if self.type is self.PRIME_TIME_WITH_DURATION:
                        return '%s - %s (%s)  %s' % (begin,
                         end,
                         duration,
                         title)
                    elif self.type is self.PRIME_TIME_ONLY_DURATION:
                        return duration
                    elif self.type == self.PRIME_TIME_NO_DURATION:
                        return '%s - %s  %s' % (begin, end, title)
                    else:
                        return ''
            return ''
        else:
            if self.type is self.NEXT_NAME or self.type is self.NEXT_TIME_DURATION or self.type is self.NEXT_DESCRIPTION or self.type is self.NEXT_NAMEWT:
                reference = self.source.service
                info = reference and self.source.info
                if info is not None:
                    eventNext = self.epgcache.lookupEvent(['IBDCTSERNX', (reference.toString(), 1, -1)])
                    if eventNext:
                        if self.type is self.NEXT_NAME or self.type is self.NEXT_NAMEWT or self.type is self.NEXT_TIME_DURATION:
                            t = localtime(eventNext[0][1])
                            duration = _('%d min') % (int(0 if eventNext[0][2] is None else eventNext[0][2]) / 60)
                            if len(eventNext[0]) > 4 and eventNext[0][4]:
                                if self.type is self.NEXT_NAME:
                                    return '%02d:%02d (%s) %s' % (t[3],
                                     t[4],
                                     duration,
                                     eventNext[0][4])
                                elif self.type is self.NEXT_TIME_DURATION:
                                    return '%02d:%02d (%s)' % (t[3], t[4], duration)
                                else:
                                    return '%s' % eventNext[0][4]
                            else:
                                return ''
                        elif self.type is self.NEXT_DESCRIPTION:
                            for i in (6, 5, 4):
                                if len(eventNext[0]) > i and eventNext[0][i]:
                                    if 'EPG-SAT.DE' in eventNext[0][i]:
                                        return ''
                                    return '%s' % eventNext[0][i]

                    else:
                        return ''
                else:
                    return ''
            elif self.type is self.NEXT_EVENT_LIST or self.type is self.NEXT_EVENT_LISTWT or self.type is self.NEXT_EVENT_LIST2 or self.type is self.NEXT_EVENT_LISTWT2 or self.type is self.NEXT_NAME_NEXT or self.type is self.NEXT_NAME_NEXTWT:
                reference = self.source.service
                info = reference and self.source.info
                countitem = 10
                if info is not None:
                    eventNext = self.epgcache.lookupEvent(['IBDCT', (reference.toString(),
                      0,
                      -1,
                      -1)])
                    if self.type is self.NEXT_NAME_NEXT or self.type is self.NEXT_NAME_NEXTWT:
                        countitem = 4
                    if eventNext:
                        listEpg = []
                        i = 0
                        for x in eventNext:
                            if i > 0 and i < countitem:
                                if x[4]:
                                    t = localtime(x[1])
                                    if self.type is self.NEXT_EVENT_LIST or self.type is self.NEXT_EVENT_LIST2 or self.type is self.NEXT_NAME_NEXT:
                                        duration = _('%d min') % (int(0 if eventNext[i][2] is None else eventNext[i][2]) / 60)
                                        listEpg.append('%02d:%02d (%s) %s' % (t[3],
                                         t[4],
                                         duration,
                                         x[4]))
                                    else:
                                        listEpg.append('%02d:%02d %s' % (t[3], t[4], x[4]))
                            i += 1

                        if self.type is self.NEXT_EVENT_LIST2 or self.type is self.NEXT_EVENT_LISTWT2 or self.type is self.NEXT_NAME_NEXT or self.type is self.NEXT_NAME_NEXTWT:
                            if len(listEpg) > 1:
                                listEpg.pop(0)
                            else:
                                return ''
                            return '\n'.join(listEpg)
                        else:
                            return '\n'.join(listEpg)
                    else:
                        return ''
                else:
                    return ''
            else:
                return ''
            return

    text = property(getText)