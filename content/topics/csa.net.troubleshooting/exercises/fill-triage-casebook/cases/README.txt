The triage desk's cases: six tickets from the shop's networks, each in a
folder of its own with what the on-call engineer saved.

  ticket.txt    the ticket, in the words of whoever raised it, and the machines
  mtr.txt       an mtr report on the path
  capture.txt   a tcpdump -nn capture at one machine
  journal.txt   the logs of the services involved
  session.txt   the commands the engineer typed, each after a $, with what
                each printed

Every file but the ticket is real output, captured on 2026-11-12 in this
module's labs; the times are those labs' clocks. causes.txt lists the causes a case may name.
The sheet to fill in is ~/triage.txt.
