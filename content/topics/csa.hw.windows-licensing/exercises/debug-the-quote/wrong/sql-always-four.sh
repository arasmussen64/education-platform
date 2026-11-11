# Wrong: the benefit and the host fixed, and SQL Server "fixed" by charging
# every SQL Server VM for 4 vCPUs, whatever its size. Both of the learner's
# inventories come out right, because every SQL Server in them that pays a
# licence has 2 or 4 vCPUs; a bigger one without Software Assurance is
# charged for 4 vCPUs it has more than.
sed -i -e 's/rate\[\$5\] \* \$3 \* hours/rate[$5] * 4 * hours/' \
  -e 's/benefit = (\$4 == "windows")/benefit = ($6 == "yes")/' \
  -e 's|host_price \* used / slots \* hours|host_price * hours|' ~/quote/make-quote
~/quote/make-quote ~/quote/inventory.csv
