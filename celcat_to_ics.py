#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
#
# Copyright © 2016 Mael Valais <mael.valais@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Usage: celcat_to_ics.py [-d] [-c str[,...]] [-g str[,...]] [-o OUTPUT] (- | INPUT)

INPUT           is the celcat .xml you want to parse
- --stdin       use stdin for input instead of INTPUT
-o OUTPUT       specify output .ics file (uses stdout by default)
-c str[,...]    only keep courses where name contains "str"; you can give
                multiple filtering strings, separate them using commas
-g str[,...]    only keep courses where group contains "str"; same as above
-d              turn on debugging (will display the cmd-line arguments given)
-h --help       show this

"""

import re # regex expressions for "rawweeks"
from datetime import datetime,timedelta
from sys import stdout,stdin

try:
    from icalendar import Calendar, Event, vDatetime, Timezone, TimezoneDaylight, TimezoneStandard
    from lxml import etree                           # `pip3 install lxml`
    from docopt import docopt                        # `pip3 install docopt`
except ImportError:
    print("=================================================================")
    print("IMPORTANT: you must install icalendar, lxml and docopt. Run this:")
    print("   pip3 install icalendar lxml docopt                            ")
    print("=================================================================")
    raise

def parse_celcat(f,g_filters,c_filters):
    """
    :param f: the already open XML CELCAT file
    :param g_filters: single string with comma-separated patterns to filter groups.
           With "TP11,TP12", "EDG1RTP12" is returned
    :param c_filters: same but for the courses
    :return: a list of icalendar.Event
    """
    xml = etree.parse(f)
    week_map = dict()
    for span in xml.xpath("/timetable/span"):
        # CELCAT gives at the beginning of XML in <span> the mapping between
        # the date of beginning of week X and the rowix (which
        # corresponds to the position of the "Y" in <rawweek>).
        # So when I want to know the date of an event: 1- find the position
        # of Y in NNNYNNNNNNN. 2- find the begin date of the corresponding week
        # which was given by rawix in the span block. 3- add "day" to this date
        week_map[int(span.get("rawix"))] = datetime.strptime(span.get("date"),'%d/%m/%Y')
    events = []
    for ev in xml.xpath("/timetable/event"):
        ev_out = Event()
        groups = [a.text for a in ev.findall("resources/group/item")]
        course = ev.find("resources/module/item").text
        if (g_filters is None or any(any(str in g for g in groups) for str in g_filters))\
        and(c_filters is None or any(str in course for str in c_filters)):
            ev_out['SUMMARY'] = course
            ev_out['LOCATION'] =\
                ev.find("resources/room/item").text if ev.find("resources/room/item")!=None else ""
            date = week_map[re.search("Y",ev.find("rawweeks").text).start()+1] + \
                            timedelta(days=int(ev.find("day").text))
            starttime = datetime.combine(date, datetime.strptime(ev.find("starttime").text, '%H:%M').time())
            endtime = datetime.combine(date, datetime.strptime(ev.find("endtime").text, '%H:%M').time())
            ev_out["DTSTART"] = vDatetime(starttime).to_ical()
            ev_out["DTEND"] = vDatetime(endtime).to_ical()
            ev_out["UID"] = ev.attrib.get("id") + str(len(events)) # hand-crafted UID
            ev_out["CREATED"] = vDatetime(datetime.now()).to_ical()
            ev_out["LAST-MODIFIED"] = vDatetime(datetime.now()).to_ical()
            ev_out["DESCRIPTION"] = \
                ("Remarques:\n" + ev.find("notes").text + "\n" if ev.find("notes") is not None else "")\
                + "Groupes:\n"+"".join("%s\n" % g for g in groups)
            ev_out["STATUS"] = "CONFIRMED"
            events.append(ev_out)
        calname = xml.xpath("/timetable/option/subheading")[0].text
    return events, calname

def main():
    args = docopt(__doc__,version=
        "Utility for extracting courses from a celcat xml to a *plain* "
        "courses file (see Nathanael\'s scripts)")
    if args["-d"]: print(args)

    input_file = stdin if args["-"] else open(args["INPUT"],'r')
    output_file = stdout if args["-o"] is None else open(args["-o"],'w')

    group_filters = args["-g"].split(",") if args["-g"] is not None else None
    course_filters = args["-c"].split(",") if args["-c"] is not None else None

    events,calname = parse_celcat(input_file,group_filters,course_filters)
    cal = Calendar()
    cal["VERSION"] = 2.0
    cal["PRODID"] = "Some proid"
    cal["CALSCALE"] = "GREGORIAN"
    cal["METHOD"] = "PUBLISH"
    cal["X-WR-CALNAME"] = calname
    cal["X-WR-TIMEZONE"] = "Europe/Paris"
    tz = Timezone()
    tz["TZID"] = "Europe/Paris"
    tz["X-LIC-LOCATION"] = "Europe/Paris"

    tz_day = TimezoneDaylight()
    tz_day["DTSTART"] = "19810329T020000"
    tz_day["TZOFFSETFROM"] = "+0100"
    tz_day["TZOFFSETTO"] = "+0200"
    tz_day["TZNAME"] = "CEST"
    tz_day["RRULE"] = "FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU"

    tz_std = TimezoneStandard()
    tz_std["DTSTART"] = "19961027T030000"
    tz_std["TZOFFSETFROM"] = "+0200"
    tz_std["TZOFFSETTO"] = "+0100"
    tz_std["TZNAME"] = "CET"
    tz_std["RRULE"] = "FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU"

    tz.add_component(tz_day)
    tz.add_component(tz_std)
    cal.add_component(tz)

    for e in events:
        cal.add_component(e)

    output_file.write(cal.to_ical().decode("utf-8")
        .replace('\\r\\n', '\n')
        .replace('\;', ';')
        .strip())

if __name__ == "__main__":
    main()
