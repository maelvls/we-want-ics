celcat_to_ics, the tiny python parser for getting rid of this hiddeous
and unusable CELCAT Timetable from the 90's and that does even have .ics
export (at least not on edt.univ-tlse3.fr)

You just have to find the CELCAT url of the `.html` for your group/course, 
replace the ending `.html` with `.xml` and run it.

## Example

    curl https://edt.univ-tlse3.fr/FSI/FSImentionL/Math/g29617.xml\
    | ./celcat_to_ics.py --stdin -g TPA11,TPA12 -c Info > L1_CUPGE_TDA1.ics
In this example, with want to get the `.ics` from the `.xml` CELCAT Timetable.
We first fetch the `.xml` and pass it to the parser; the options are:
- `-g TPA11,TPA12` selects the events where the group name has "TPA11" or 
  "TPA12" in it.
- `-c Info` selects the events where the event name (or course/class name)
  has "Info" in it.



## Features

1. allows you to filter on the courses names, e.g.,
   if we have the courses called
      
        EPTRI1A1 - Informatique
        EPNFM1A1 - Mathématiques
        EPPCP1C1 - Lumière et couleur
   
   and that you use the argument
   
        -g Math,Info
   
   then the resulting `.ics` will only contain the courses *Informatique*
   and *Mathématiques*. You can even be clever and get the same result
   only using one pattern matching:
      
        -g matique
      
2. allows you to filter on the group names; this is really useful
   when you are a professor assigned to practical works (TP in french)
   and you want to track only the groups you care about.
   Say we have numerous course names:
      
        L1 Chimie s1 - TDA1
        L1 Chimie s1 - TDA2
        L1 Chimie s1 - TDA3
        L1 Chimie s1 - TDA4
        L1 Chimie s1 - TDA5
        L1 Chimie s1 - TDA6
        L1 Chimie s1 - TPB11
        L1 Chimie s1 - TPB21
        L1 CUPGE s1 - TDA1
        L1 CUPGE s1 - TDA2
        L1 CUPGE s1 - TDA3
   We only want to track the classes where the group A3 and the group
   A6. We do:
      
        -c A3,A6
      
   Note that for now, no space is allowed in the filter expression.
   Also note that `-c` and `-g` are used in conjunction (logical AND).


## Restrictions

- only accepts one XML/CELCAT file in input, no batch-like calendar yet
- filtering groups and courses is limited to expressions without spaces
- it is not (yet) possible to change the group and class names to custom and friendlier names


## Dependencies

Three `pip` packages are used: `icalendar`, `lxml` and `docopt`. To install them:
    
    pip3 install icalendar lxml docopt


## Performance

Parsing one average `.xml` CELCAT file takes about 100ms for a 3460 lines XML file.
Example with two filters (more filters => heavier computation)
    
    ./celcat_to_ics.py g29617.xml -g TPA11 -c Info  
        -> 0,13s user 0,02s system 94% cpu 0,156 total

When parsing with a little more filters, the execution is slightly longer:
    
    ./celcat_to_ics.py g29617.xml -g TPA11,TD,TP -c Info,Math  
        -> 0,15s user 0,03s system 91% cpu 0,197 total


## Detailed usage

```
celcat_to_ics.py [-d] [-c str[,...]] [-g str[,...]] [-o OUTPUT] (INPUT | --stdin)

INPUT           is the celcat .xml you want to parse
-s --stdin      use stdin for input instead of INTPUT
-o OUTPUT       specify output .ics file (uses stdout by default)
-c str[,...]    only keep courses where name contains "str"; you can give
                multiple filtering strings, separate them using commas
-g str[,...]    only keep courses where group contains "str"; same as above
-d              turn on debugging (will display the cmd-line arguments given)
-h --help       show this
```
