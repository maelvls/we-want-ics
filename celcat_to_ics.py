#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
#
# Copyright © 2016 Mael Valais <mael.valais@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Usage: celcat_to_ics.py [-d] [-r filter] [-o OUTPUT] (- | INPUT ...)

-h --help       show this
INPUT           is the celcat .xml you want to parse
-               use stdin for input instead of INTPUT
-o OUTPUT       specify output .ics file (uses stdout by default)
-d              turn on debugging (will display the cmd-line arguments given)
-r filter       turn on regex filtering

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

def parse_celcat(f, filter=[], debug=False):
    """
    :param filter: the already open XML CELCAT file
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

    if debug:
        print("Filter: "+"\n or ".join(["(group=(" + " ".join([comma for comma in plus[0]])
             + ") and course=(" + " or ".join([comma for comma in plus[1]]) + "))" for plus in filter]))
    events = []
    for ev in xml.xpath("/timetable/event"):
        ev_out = Event()
        groups = [a.text for a in ev.findall("resources/group/item")]
        course = ev.find("resources/module/item").text

        # See comment in main() for more precision; as a remainnder:
        # ((TPA31 or TPA32) and (Info or Logique)) or (TPA11 and Info)

        if any(any(any(comma in g for g in groups) for comma in plus[0]) and any(comma in course for comma in plus[1]) for plus in filter):
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
    args = docopt(__doc__)
    if args["-d"]: print(args)

    input_file = stdin if args["-"] is None else [open(i,'r') for i in args["INPUT"]]
    output_file = stdout if args["-o"] is None else open(args["-o"],'w')

    # :filter has the form "TPA31,TPA32:Info,Logique+TPA11:Info"
    # It becomes filter[+ separated items (OR)][0=groups,1=courses)][, separated items (OR)]
    # <=> ((TPA31 or TPA32) and (Info or Logique)) or (TPA11 and Info)
    #filter = args["-r"].split("+").split(",") if args["-r"] is not None else None
    filter = [[x.split(",") for x in e.split(":")] for e in args["-r"].split("+")]

    cal = Calendar()
    for i in input_file:
        events,calname = parse_celcat(i,filter,args["-d"])
        for e in events:
            cal.add_component(e)

    cal["VERSION"] = 2.0
    cal["PRODID"] = "Some proid"
    cal["CALSCALE"] = "GREGORIAN"
    cal["METHOD"] = "PUBLISH"
    cal["X-WR-CALNAME"] = "Calendar"
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

    output_file.write(cal.to_ical().decode("utf-8")
        .replace('\\r\\n', '\n')
        .replace('\;', ';')
        .strip())

if __name__ == "__main__":
    main()
