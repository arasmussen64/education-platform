The triage desk's cases: six tickets from the shop's networks, each in a
folder of its own with what the on-call engineer saved.

  ticket.txt    the ticket, in the words of whoever raised it, and the machines
  monitor.log   the shop's monitor over the same minutes: one line for each
                page it loaded, in the format of Follow the method's monitor,
                  TIME URL ADDRESSES STATUS SECONDS exit=N
                TIME is when the load ended, ADDRESSES the addresses curl
                tried, in order, STATUS the HTTP status (000 when there was
                none), SECONDS how long the load took, and N curl's exit
                status. It gives every load 5 seconds (curl --max-time 5).
                Each ticket says where its monitor runs and what it loads.
  mtr.txt       an mtr report on the path
  capture.txt   a tcpdump -nn capture at one machine
  journal.txt   the logs of the services involved
  session.txt   the commands the engineer typed, each after a $, with what
                each printed

mtr.txt, capture.txt, journal.txt and session.txt are real output, captured
on 2026-11-12 in this module's labs; the times are those labs' clocks. The
tickets and the monitor logs are constructed: no monitor ran in those labs
that day, so each monitor.log was written afterwards, line by line, as that
monitor would have written it, to fit its case's clock and its other files.
causes.txt lists the causes a case may name.
The sheet to fill in is ~/triage.txt.
