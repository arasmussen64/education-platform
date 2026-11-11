# Wrong: two of the three faults fixed (SQL Server's minimum, who gets the
# benefit), and the host still charged for the share of its slots in use. A
# dedicated host is billed whole, however many VMs run on it.
sed -i -e 's/rate\[\$5\] \* \$3 \* hours/rate[$5] * ($3 < 4 ? 4 : $3) * hours/' \
  -e 's/benefit = (\$4 == "windows")/benefit = ($6 == "yes")/' ~/quote/make-quote
~/quote/make-quote ~/quote/inventory.csv
