# Wrong: SQL Server and the benefit fixed, and the host line dropped instead
# of priced. The two patient-records VMs still have to run somewhere: the
# host is part of the bill.
sed -i -e 's/rate\[\$5\] \* \$3 \* hours/rate[$5] * ($3 < 4 ? 4 : $3) * hours/' \
  -e 's/benefit = (\$4 == "windows")/benefit = ($6 == "yes")/' \
  -e '/if (host != "") line("host"/d' ~/quote/make-quote
~/quote/make-quote ~/quote/inventory.csv
