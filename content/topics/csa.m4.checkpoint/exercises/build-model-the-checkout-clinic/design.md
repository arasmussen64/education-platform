# Westbrook Clinic: the payment desk

Westbrook Clinic is moving its patients' payments to a payment provider,
PayHub. Patients pay their bills online, and patients who come in pay at
reception with a card. This note describes the design as it stands,
before its security review.

## The parts

- `patient`: a patient's browser, anywhere on the internet.
- `psp`: PayHub, the payment provider: its hosted payment page and its
  API. PayHub runs both, and is assessed against PCI DSS itself.
- `portal`: the patient portal, on a server in the clinic's cloud
  network. To pay a bill, it sends the patient's browser to PayHub's
  hosted payment page, where the card is typed, with the invoice's number
  and amount. After the payment, PayHub sends the browser back to the
  portal's page `/paid?invoice=N&status=ok`, and the portal marks that
  invoice paid on what the page's address says alone: it never asks PayHub.
- `billing`: makes the invoices, and emails each patient a link to theirs.
  The link is the portal's address, `/invoice/`, and the invoice's number,
  and invoice numbers count up one at a time. The page shows the invoice
  (the patient's name and address, the treatment and the amount) to
  anyone who opens the link, with no sign-in. It runs in the clinic's
  cloud network, beside `portal`.
- `invoices-db`: the invoices. It is in the clinic's cloud network, and
  `billing` reads and writes it with the database's administrator account.
- `terminal`: the card terminal at reception. A card is tapped or
  inserted, and the terminal sends it to PayHub over its own link, which
  PayHub and the terminal authenticate both ways. It has an admin page,
  reached from the office network, and its admin password is still the
  one its maker ships with every terminal. In June its maker published an
  advisory for a flaw in its software that lets someone on its network
  read what it handles, and a fix; the fix has not been installed.
- `reception-pc`: the reception desk's PCs. Receptionists read their email
  on them, and start each payment on the terminal from them.

## The networks

The clinic's cloud network holds `portal`, `billing` and `invoices-db`.
The office network at reception holds `terminal` and `reception-pc`, with
nothing filtering between them. Nothing connects the office network to
the cloud network, and no card data goes to the cloud network.

## The flows

- `f1`, from `patient` to `portal`: booking, and starting a payment.
- `f2`, from `patient` to `psp`: paying on PayHub's hosted page.
- `f3`, from `psp` to `portal`: PayHub sends the browser back with the result.
- `f4`, from `portal` to `billing`: an invoice looked up, and marked paid.
- `f5`, from `patient` to `billing`: an invoice opened from its emailed link.
- `f6`, from `billing` to `invoices-db`: invoices read and written.
- `f7`, from `terminal` to `psp`: a card payment at reception.
- `f8`, from `reception-pc` to `terminal`: a payment started, and the
  terminal's admin page.

## Already in place

HTTPS everywhere. The cloud's load balancer limits how many requests one
address can send. Two named administrators can reach the cloud network's
database.

## The scales

Likelihood. 3: anyone on the internet could do it, with no account and
nothing stolen first. 2: it needs something first, such as a place on the
clinic's office network, a phished receptionist's PC, or a supplier's
system. 1: it needs an administrator's rights, or someone standing at the
machine.

Impact. 3: card numbers are exposed, or money is paid out or sent
elsewhere. 2: one patient's bill or details are exposed or falsified (a
bill marked paid without being paid counts here). 1: a nuisance, with
nothing lost.
