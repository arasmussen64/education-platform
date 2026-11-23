# Quickprint: the counter and the uploads

Quickprint is a print shop. Customers upload their files from home, and
pay at the counter with a card, or by a payment link that the payment
provider, PayLink, emails them. This note describes the design as it
stands, before its security review.

## The parts

- `customer`: a customer's browser, anywhere on the internet.
- `psp`: PayLink, the payment provider: its payment page, its card
  readers' service and its API. PayLink runs them, and is assessed against
  PCI DSS itself.
- `till-pc`: the till at the counter, a PC with PayLink's card reader
  plugged into it. A card's details go from the reader through the till
  PC to PayLink, over a link PayLink and the reader authenticate both ways.
  Staff sign in to the till, and every member of staff types the same
  four-digit PIN, which has not changed since the shop opened. A signed-in
  till can make refunds to any card.
- `print-server`: the print room's job server. It fetches a job's files
  from the uploads bucket with a key that can only read, and takes paid
  jobs from the till without asking who sends them.
- `directory`: the staff sign-in service, in Quickprint's cloud account.
  It checks the PIN the till sends, over HTTPS, and keeps a log.
- `files`: the bucket in Quickprint's cloud account where customers'
  uploads are kept. It only takes new files, and anyone can list it and
  download every file in it, with no sign-in.

## The networks

The shop floor's network holds `till-pc` and `print-server`, with nothing
filtering between them. Quickprint's cloud account holds `directory` and
`files`.

## The flows

- `f1`, from `customer` to `files`: a file uploaded.
- `f2`, from `till-pc` to `psp`: a card payment at the counter.
- `f3`, from `till-pc` to `directory`: a member of staff signs in to the till.
- `f4`, from `print-server` to `files`: a job's files fetched.
- `f5`, from `till-pc` to `print-server`: a paid job sent to print.
- `f6`, from `customer` to `psp`: paying by the link PayLink emails.

## Already in place

HTTPS everywhere.

## The scales

Likelihood. 3: anyone on the internet could do it, with no account and
nothing stolen first. 2: it needs something first, such as a place on the
shop floor's network, or a PIN a member of staff knows. 1: it needs an
administrator's rights.

Impact. 3: card numbers are exposed, or money is paid out of the shop's
account. 2: one customer's files or details are exposed or changed.
1: a nuisance, with nothing lost.
