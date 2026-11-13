The print shop's address plan
============================

The task
--------
The print shop is building its estate in two clouds, AWS and Google
Cloud, two regions in each, joined to its one data centre. Before the
first network is made, it needs an address plan that will last five years.
Fill in ~/plan/plan.csv: for every row, its IPv4 block and its IPv6 block.

The checks hold the plan to the rules below, and work every right answer
out from sites.csv and policy.txt themselves, so any layout that keeps the
rules passes. This folder is read-only, and the checks notice a change.

The files
---------
sites.csv: one line a site (here two regions in each cloud), with the columns
  site                    its name, as the plan's rows name it
  kind                    region (a cloud region) or dc (a data centre)
  cloud                   aws, azure or gcp for a region; onprem for a data centre
  subnets_today           how many subnets the region has today
  hosts_per_subnet_today  how many machines the busiest of them has today
  (a data centre's last two cells are empty: it keeps the block it has)

policy.txt: one setting a line, name=value
  ipv4_space        the IPv4 space every IPv4 block comes from
  in_use            a block already in use, and who uses it (one a line)
  host_growth       how many times today's machines each subnet must hold in five years
  subnet_growth     how many times today's subnets each region must hold in five years
  summary_room      how many times the space its regions' blocks take a cloud's summary must hold
  reserved_<cloud>  the addresses that cloud keeps back in every subnet
  ipv6_space        the IPv6 block every IPv6 summary comes from
  ipv6_site         the prefix length of a site's IPv6 block
  ipv6_summary      the prefix length of a summary's IPv6 block
  ipv6_gcp_pool     the pool Google Cloud gives a network's internal IPv6 from
  ipv6_gcp_network  the prefix length of the block Google Cloud gives a network

The plan's rows (~/plan/plan.csv: name,ipv4,ipv6)
------------------------------------------------
  aws              AWS's summary: one block that holds all its regions
  gcp              Google Cloud's summary: one block that holds all its regions
  <cloud>-<place>  a cloud region: one VPC or VNet's address space
  onprem           the data centres' summary
  dc-...           a data centre

The rules
---------
1. Every cell is a block written as its network address (10.2.64.0/19,
   not 10.2.65.0/19).
   The gcp-* regions' IPv6 cells are - (rule 7); every other cell has a
   block.
2. A region's IPv4 block is the smallest that holds, five years from now,
   subnet_growth times today's subnets, each subnet the smallest block
   that holds host_growth times today's machines plus the addresses its
   cloud keeps back. Exactly that size: not smaller, and not bigger.
3. Every IPv4 block is inside ipv4_space. No two sites overlap, no region
   and no cloud summary overlaps a block in use, and no two summaries
   overlap.
4. The data centres keep the blocks they have (policy.txt's in_use lines
   with their names), and onprem is the smallest block that holds them all.
5. Each cloud's regions sit inside that cloud's summary, and the summary is
   the smallest block that holds summary_room times the space its regions'
   blocks take.
6. IPv6: every site's block (regions and data centres) is ipv6_site long and
   every summary (the clouds' and onprem) ipv6_summary long. The summaries
   are inside ipv6_space and apart from each other, each site is inside its
   own summary, and no two sites overlap. Every IPv6 prefix length is a
   multiple of 4, a nibble boundary: each hex digit is 4 bits, so a prefix
   that ends on a digit's edge keeps the plan readable and lines up with
   reverse DNS.
7. gcp's IPv6 cell is the network's internal IPv6 block: an
   ipv6_gcp_network-long block inside ipv6_gcp_pool. You choose which one.
   The gcp-* regions' IPv6 cells are -, because Google Cloud picks each
   subnet's /64 from that block itself.

Where the clouds differ (each read on 2026-11-12)
-------------------------------------------------
- AWS keeps back 5 addresses in every subnet: the first four and the last.
  A VPC's and a subnet's IPv4 blocks are /16 to /28; IPv6 subnets are /44
  to /64, in steps of 4.
    https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html
- Google Cloud keeps back 4 addresses in every subnet: the first two and
  the last two. Its smallest IPv4 range is a /29. A network's internal
  IPv6 is a /48 from fd20::/20, which Google Cloud picks or you choose,
  and Google Cloud picks each subnet's /64 from it itself.
    https://docs.cloud.google.com/vpc/docs/subnets
- RIPE-690, the operators' guide to IPv6 prefix sizes, suggests a /48 for
  a business site and prefix lengths on nibble boundaries.
    https://www.ripe.net/publications/docs/ripe-690/

Tools
-----
  plan-show        prints your plan as a tree, each block with its first and
                   last address and how big it is. It checks nothing.
  ipcalc, sipcalc  the calculators from the CIDR topic (ipcalc -b BLOCK).
  nano ~/plan/plan.csv   to fill in the plan.
