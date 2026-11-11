The price file, 2026-11.csv

Each line after the header is one instance type: the cloud, the type's name,
its architecture (x86-64 or arm64), its number of vCPUs, and its on-demand
list price for Linux in US dollars an hour. The lines that start with # say
where and when the prices were read: on 2026-11-11, from AWS's price file
for US East (N. Virginia), Azure's Retail Prices API for East US, and Google
Cloud's price page for Iowa (us-central1).

On-demand means paying by the hour with no commitment; the clouds sell the
same machines for less if you commit to a year or more, or accept that they
can be taken back. Prices differ by region and change over time, so a file
like this is only true of the day it was read. Don't edit it: the checks
confirm it's unchanged.
