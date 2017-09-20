#! /bin/bash
#
# gen_cal.sh
# Copyright (C) 2016 Maël Valais <mael.valais@gmail.com>
#
#

# Exit on any error in the script
set -e

ICS=.
if [ ! -d "$ICS" ]; then mkdir "$ICS"; fi

pip3 -q install icalendar lxml docopt || exit 1

cat > $ICS/.htaccess <<-'EOF'
Options +Indexes
EOF

# Note for myself: in order to 'see' any calendar online without
# knowning the 'g432432.html' ending, just add 'finder.html' instead
#    https://edt.univ-tlse3.fr/FSI/2017_2018/M1/M1_INF_SIAME/g241742.xml
#    https://edt.univ-tlse3.fr/FSI/2017_2018/M1/M1_INF_SIAME/finder.html

curl -s -O https://edt.univ-tlse3.fr/FSI/2017_2018/M1/M1_INF_SIAME/g241742.xml
curl -s -O https://edt.univ-tlse3.fr/FSI/2017_2018/M1/M1_INF_IHM/g241638.xml
curl -s -O https://edt.univ-tlse3.fr/FSI/2017_2018/M1/M1_INF_DL/g241675.xml
curl -s -O https://edt.univ-tlse3.fr/FSI/2017_2018/M1/M1_INF_IARF/g241496.xml
curl -s -O https://edt.univ-tlse3.fr/FSI/2017_2018/L1/L1_PS/g220501.xml
$PWD/celcat_to_ics.py g*.xml -r "M1 INF-IARF s1 TPA,M1 INF-IHM s1 TPA:compilation+M1 INF-SIAME s1 TPA,M1 INF-DL s1 TPA11:Algorithmique avancée+L1 PS s1 TPA2:EPMAS1D1 - Informatique" -o "$ICS"/mael.ics -v

# Check the permissions
find "$ICS" \( -type d -exec chmod ugo+rx {} \; \) -o \( -type f -exec chmod ugo+r {} \; \)
