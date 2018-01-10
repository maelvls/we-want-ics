#! /bin/bash
#
# gen_cal.sh
# Copyright (C) 2016 Maël Valais <mael.valais@gmail.com>
#
#

# Exit on any error in the script
set -e

ICS=/usr/local/WWW-personnel/Mael.Valais/ics/
if [ ! -d "$ICS" ]; then mkdir "$ICS"; fi

pip3 -q install icalendar lxml docopt || exit 1

cat > $ICS/.htaccess <<-'EOF'
Options +Indexes
EOF

cd $(dirname "$0")

# Note for myself: in order to 'see' any calendar online without
# knowning the 'g432432.html' ending, just add 'finder.html' instead
#    https://edt.univ-tlse3.fr/FSI/2017_2018/M1/M1_INF_SIAME/g241742.xml
#    https://edt.univ-tlse3.fr/FSI/2017_2018/M1/M1_INF_SIAME/finder.html

#curl -s -O https://edt.univ-tlse3.fr/FSI/2017_2018/M1/M1_INF_SIAME/g241742.xml
#curl -s -O https://edt.univ-tlse3.fr/FSI/2017_2018/M1/M1_INF_IHM/g241638.xml
#curl -s -O https://edt.univ-tlse3.fr/FSI/2017_2018/M1/M1_INF_DL/g241675.xml
#curl -s -O https://edt.univ-tlse3.fr/FSI/2017_2018/M1/M1_INF_IARF/g241496.xml
#curl -s -O https://edt.univ-tlse3.fr/FSI/2017_2018/L1/L1_PS/g220501.xml

curl -s -O https://edt.univ-tlse3.fr/FSI/2017_2018/L1/L1_SF/g254186.xml
curl -s -O https://edt.univ-tlse3.fr/FSI/2017_2018/L1/L1_SF/g254187.xml
curl -s -O https://edt.univ-tlse3.fr/FSI/2017_2018/L1/L1_SF/g254189.xml
curl -s -O https://edt.univ-tlse3.fr/FSI/2017_2018/L1/L1_SF/g254190.xml
# To search the courses with 'Logique 1' inside:
# curl https://edt.univ-tlse3.fr/FSI/2017_2018/L1/L1_SF/finder.xml | grep href= | cut -d'"' -f2 | while read l; echo $l; do curl -s https://edt.univ-tlse3.fr/FSI/2017_2018/L1/L1_SF/$l | grep EPINF2C1; done

$PWD/celcat_to_ics.py g*.xml -r \
	"L1 PM s2 TDA4:Logique 1" -o "$ICS"/mael.ics -v

# Check the permissions
find "$ICS" \( -type d -exec chmod ugo+rx {} \; \) -o \( -type f -exec chmod ugo+r {} \; \)
