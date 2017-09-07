#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
#
# Copyright © 2016 Mael Valais <mael.valais@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Usage: celcat_to_ics.py [options] [-r FILTER] [-o OUTPUT] (- | INPUT ...)
       celcat_to_ics.py --version
       celcat_to_ics.py (--help | -h)

-h, --help      show this
INPUT           is the celcat .xml you want to parse (you can give multiple)
-               use stdin for input instead of INTPUT
-o OUTPUT       specify output .ics file (uses stdout by default)
-r FILTER       turn on regex filtering
--log FILE      logs output to a file [default: output.out]
-v              verbose mode: displays the arguments given
                and a "human-readable" version of FILTER

FILTER is a string of the form
        "G1[,G2...]:C1[,C2...][+...]"
    which translates to "select events that have G1 or G2 in their group name
    AND that have C1 or C2 in their course name. The "+" separates multiple of
    these filters and behaves like a OR.

    Example:
        "L1 Chimie s1 - TPA12:Info+\
        L1 CUPGE s1 - TPA12:Info+\
        L1 Info s1 - TPB31:Info+\
        L2 Info s1 - TPA32:Syst+\
        L2 Info s1 - TPA41,L2 Info s1 - TPA42,L2 Info s1 - TPA52:Logique"

    Note: "+",":" and "," are reserved keywords. You can use spaces. You don't
    need to enter the full group/course name (only needs to be a part of it).
"""

import re # regex expressions for "rawweeks"
from datetime import datetime,timedelta
from sys import stdout,stdin
from quicklog import * # this is my friend's, Eric Moyer; depends on `pip3 install colorama`

__all__ = ['docopt','icalendar','lxml','colorama']
__version__ = '0.1.0'

try:
    from icalendar import Calendar, Event, vDatetime, Timezone, TimezoneDaylight, TimezoneStandard
    from lxml import etree                           # `pip3 install lxml`
    from docopt import docopt                        # `pip3 install docopt`
except ImportError:
    print("=================================================================")
    print("IMPORTANT: some pip3 packages are missing. Run this:             ")
    print("   pip3 install "," ".join(__all__),"                            ")
    print("=================================================================")
    raise

def parse_celcat(f, filter=[]):
    """
    :param f: the already open XML CELCAT file
    :param filter: single string with comma-separated patterns to filter groups.
           With "TP11,TP12", "EDG1RTP12" is returned
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
        category = ev.find("category").text
        groups = [a.text for a in ev.findall("resources/group/item")]
        course = ev.find("resources/module/item")
        course = course.text if course is not None else None

        # See comment in main() for more precision; as a remainnder:
        # ((TPA31 or TPA32) and (Info or Logique)) or (TPA11 and Info)
        if (filter == []
            or (course is not None
                and any( any(any(comma in g for g in groups) for comma in plus[0])
                    and any(comma in course for comma in plus[1])
                for plus in filter)
                )
            ):
            ev_out['SUMMARY'] = course
            ev_out['LOCATION'] =\
                "; ".join([a.text for a in ev.findall("resources/room/item")]) if ev.find("resources/room/item")!=None else ""
            date = week_map[re.search("Y",ev.find("rawweeks").text).start()+1] + \
                            timedelta(days=int(ev.find("day").text))
            starttime = datetime.combine(date, datetime.strptime(ev.find("starttime").text, '%H:%M').time())
            endtime = datetime.combine(date, datetime.strptime(ev.find("endtime").text, '%H:%M').time())
            ev_out["DTSTART"] = vDatetime(starttime).to_ical()
            ev_out["DTEND"] = vDatetime(endtime).to_ical()
            ev_out["UID"] = ev.attrib.get("id") + str(len(events)) # hand-crafted UID
            ev_out["CREATED"] = vDatetime(datetime.now()).to_ical()
            ev_out["LAST-MODIFIED"] = vDatetime(datetime.now()).to_ical()
            ev_out["DESCRIPTION"] = (
                ("Remarques:\n" + ev.find("notes").text + "\n" if ev.find("notes") is not None else "")
                + "Groupes:\n"+"".join("%s\n" % g for g in groups) + "\n"
                + "Generated from CELCAT on: " + datetime.now().strftime("%d-%m-%Y %H:%M")
            )
            ev_out["STATUS"] = "CONFIRMED"
            events.append(ev_out)
    calname = xml.xpath("/timetable/option/subheading")[0].text
    return events, calname

def main():
    args = docopt(doc=__doc__,version=__version__)
    log = Quicklog(application_name="celcat_to_ics",
                   enable_colored_logging=False,
                   enable_colored_printing=True,
                   log_filename=args['--log'],
                   print_level=logging.DEBUG if args['-v'] else logging.INFO,
                   logging_level=logging.DEBUG,
                   version=__version__)

    input_files = [stdin] if args["-"] else [open(i,'r') for i in args["INPUT"]]
    output_file = stdout if args["-o"] is None else open(args["-o"],'w')

    # :filter has the form "TPA31,TPA32:Info,Logique+TPA11:Info"
    # It becomes filter[+ separated items (OR)][0=groups,1=courses)][, separated items (OR)]
    # <=> ((TPA31 or TPA32) and (Info or Logique)) or (TPA11 and Info)
    # filter = args["-r"].split("+").split(",") if args["-r"] is not None else None
    filter_string = [] if args["-r"] is None else \
        [[x.split(",") for x in e.split(":")] for e in args["-r"].split("+")]
    log.begin(show=False)
    log.debug("Positional parameters:\n"+str(args)+"\n")
    l=["  course is {(" + ") or (".join([j for j in i[0]]) + ")}" +
       "\n  and group is {(" + ") or (".join([j for j in i[1]]) + ")}"
        for i in filter_string]
    log.debug("Filters:\n" + "\nOR\n".join(l))


    cal = Calendar()

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

    for i in input_files:
        events,calname = parse_celcat(i,filter_string)
        for e in events:
            cal.add_component(e)
    output_file.write(cal.to_ical().decode("utf-8")
        .replace('\\r\\n', '\n')
        .replace('\;', ';')
        .strip())

    log.end()

if __name__ == "__main__":
    main()
