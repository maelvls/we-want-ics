#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
#
# Copyright © 2016 Mael Valais <mael.valais@gmail.com>
#
# Distributed under terms of the MIT license.

"""Usage: celcat_to_ics.py [-d] [-c str[,...]] [-g str[,...]] [-o OUTPUT] (INPUT | --stdin)

INPUT           is the celcat .xml you want to parse
-s --stdin      use stdin for input instead of INTPUT
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

from icalendar import Calendar, Event, vDatetime # `pip3 install icalendar`
from lxml import etree                           # `pip3 install lxml`
from docopt import docopt                        # `pip3 install docopt`
import pdb

def find_courses(f):
    tree = etree.parse(f)
    courses=set()
    for course in tree.xpath("/timetable/event/resources/module/item"):
        courses.add(course.text)
    return set(courses)

def find_groups(f):
    tree = etree.parse(f)
    groups=set()
    for g in tree.xpath("/timetable/event/resources/group/item"):
        groups.add(g.text)
    return set(groups)

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
            ev_out.add('SUMMARY',course)
            ev_out.add('LOCATION',
                ev.find("resources/room/item").text if ev.find("resources/room/item")!=None else "")
            date = week_map[re.search("Y",ev.find("rawweeks").text).start()+1] + \
                            timedelta(days=int(ev.find("day").text))
            starttime = datetime.combine(date, datetime.strptime(ev.find("starttime").text, '%H:%M').time())
            endtime = datetime.combine(date, datetime.strptime(ev.find("endtime").text, '%H:%M').time())
            ev_out.add("DTSTART",starttime)
            ev_out.add("DTEND",endtime)
            ev_out.add("UID",ev.attrib.get("id") + str(len(events))) # hand-crafted UID
            ev_out.add("CREATED",datetime.now())
            ev_out.add("LAST-MODIFIED",datetime.now())
            ev_out.add("DESCRIPTION",
                ("Remarques:\n" + ev.find("notes").text + "\n" if ev.find("notes") is not None else "")
                + "Groupes:\n"+"".join("%s\n" % g for g in groups))
            ev_out.add("STATUS","CONFIRMED")
            events.append(ev_out)
    return events

def main():
    args = docopt(__doc__,version=
        "Utility for extracting courses from a celcat xml to a *plain* "
        "courses file (see Nathanael\'s scripts)")
    if args["-d"]: print(args)

    input_file = stdin if args["--stdin"] else open(args["INPUT"],'r')
    output_file = stdout if args["-o"] is None else open(args["-o"],'w')

    group_filters = args["-g"].split(",") if args["-g"] is not None else None
    course_filters = args["-c"].split(",") if args["-c"] is not None else None

    events = parse_celcat(input_file,group_filters,course_filters)
    cal = Calendar()
    cal.add("VERSION",2.0)
    cal.add("PRODID","-//MultiAgentSystems.org//University Calendar//EN")
    cal.add("CALSCALE","GREGORIAN")
    cal.add("METHOD","PUBLISH")
    cal.add("X-WR-CALNAME","")
    cal.add("X-WR-TIMEZONE","Europe/Paris")
    cal.add("BEGIN","VTIMEZONE")
    cal.add("TZID","Europe/Paris")
    cal.add("X-LIC-LOCATION","Europe/Paris")
    cal.add("BEGIN","DAYLIGHT")
    cal.add("TZOFFSETFROM",timedelta(hours=1)) # +0100
    cal.add("TZOFFSETTO",timedelta(hours=2)) # +0200
    cal.add("TZNAME","CEST")
    cal.add("DTSTART",vDatetime.from_ical("19961027T030000"))
    cal.add("RRULE",dict({"FREQ": "YEARLY","BYMONTH": 3, "BYDAY": "-1SU"}))
    cal.add("END", "DAYLIGHT")
    cal.add("BEGIN","STANDARD")
    cal.add("TZOFFSETFROM",timedelta(hours=2))
    cal.add("TZOFFSETTO",timedelta(hours=1))
    cal.add("TZNAME","CET")
    cal.add("RRULE",dict({"FREQ": "YEARLY", "BYMONTH": 10, "BYDAY": "-1SU"}))
    cal.add("END","STANDARD")
    cal.add("END","VTIMEZONE")
    for e in events:
        cal.add_component(e)

    output_file.write(cal.to_ical().decode("utf-8").replace('\\r\\n', '\n').strip())

if __name__ == "__main__":
    main()