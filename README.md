`celcat_to_ics.py`, the tiny python parser for getting rid of this hiddeous
and unusable CELCAT Timetable from the 90's and that does even have .ics
export (at least not on edt.univ-tlse3.fr)

You just have to find the CELCAT url of the `.html` for your group/course, 
replace the ending `.html` with `.xml` and run it.

## Example

    curl https://edt.univ-tlse3.fr/FSI/FSImentionL/Math/g29617.xml\
    | ./celcat_to_ics.py - -r "L1 Chimie s1 - TPA12:Info+L1 CUPGE s1 - TPA12:Info+\
        L2 Info s1 - TPA41,L2 Info s1 - TPA42,L2 Info s1 - TPA52:Logique" > calendar.ics
In this example, with want to get the `.ics` from the `.xml` CELCAT Timetable.
We first fetch the `.xml` and pass it to the parser.

FILTER is a string of the form
        "G1[,G2...]:C1[,C2...][+...]"
which translates to "select events that have G1 or G2 in their group name AND that have
C1 or C2 in their course name. The "+" separates multiple of these filters and behaves
like a OR.

Note: "+",":" and "," are reserved keywords. You can use spaces. You don't
need to enter the full group/course name (only needs to be a part of it).


To be able to import the resulting `ics` file into Google Calendar (or iCloud),
you need to push it to a place that serves HTML pages. The scheme would be

```
curl cal.xml  ->  celcat_to_ics.py  ->  cal.ics on apache server  -> google calendar
<------------ python server ------->   <------- html server ----->
```

My configuration is:

- I run the python script on private server at IMT;
  it runs as a cron job every once in a while (2h)
- it then pushes the `.ics` files to a [public server](math.univ-toulouse.fr/~mvalais/ics)

## TODO

- [x] accept multiple XML/CELCAT file in input for building one unique `.ics` for all your courses
- [x] allow the spaces in the filters for groups and courses
- [ ] allow a way to change the names of the courses for friendlier/handier reading on your smartphone when the original title isn't nice enough
- [ ] make sure that the user won't miss any "special" events, because filtering implies that the other events won't be shown


## Dependencies

Three `pip` packages are used: `icalendar`, `lxml` and `docopt`. To install them:
    
    pip3 install icalendar lxml docopt


## Performance

WARNING: these tests have been made on a previous version, but the performance is essentially
the same on the newest version.

Parsing one average `.xml` CELCAT file takes about 100ms for a 3460 lines XML file.
Example with two filters (more filters => heavier computation)
    
    ./celcat_to_ics.py g29617.xml -g TPA11 -c Info  
        -> 0,13s user 0,02s system 94% cpu 0,156 total

When parsing with a little more filters, the execution is slightly longer:
    
    ./celcat_to_ics.py g29617.xml -g TPA11,TD,TP -c Info,Math  
        -> 0,15s user 0,03s system 91% cpu 0,197 total


## Detailed usage

See usage in `celcat_to_ics.py`.