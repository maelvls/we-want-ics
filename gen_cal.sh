#! /bin/bash
#
# a.sh
# Copyright (C) 2016 Maël Valais <mael.valais@gmail.com>
#
#

ICS=/usr/local/WWW-personnel/Mael.Valais/ics
if [ ! -d "$ICS" ]; then mkdir "$ICS"; fi

pip3 -q install icalendar lxml docopt || exit 1

cat > $ICS/.htaccess <<-'EOF'
Options +Indexes
EOF

curl -s -O https://edt.univ-tlse3.fr/FSI/2017_2018/M1/M1_INF_SIAME/g241742.xml
curl -s -O https://edt.univ-tlse3.fr/FSI/2017_2018/M1/M1_INF_IHM/g241638.xml
$PWD/celcat_to_ics.py g*.xml -r "TPA:compilation" -o "$ICS"/mael.ics

# Check the permissions
find "$ICS" \( -type d -exec chmod ugo+rx {} \; \) -o \( -type f -exec chmod ugo+r {} \; \)
