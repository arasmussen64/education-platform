# The shop: the newsletter sign-up

The shop sends a newsletter. Visitors sign up for it on the shop's site,
and a mailing company delivers the emails. This note describes the
sign-up as it is today.

## The parts

- `visitor`: a visitor's browser or phone, anywhere on the internet.
- `signup-api`: the sign-up API. The shop runs it on its own servers, in
  its own cloud network.
- `subscribers-db`: the database of subscribers' email addresses. The
  shop runs it too, on a server in the same network.
- `mailer`: the mailing company's servers. The mailing company runs them.

## The flows

- `f1`, from `visitor` to `signup-api`: a visitor types an email address
  to subscribe. Nobody signs in. The API sends that address an email with
  a link, and adds the address to the list only when the link is opened.
- `f2`, from `signup-api` to `subscribers-db`: the API reads and writes
  the list.
- `f3`, from `signup-api` to `mailer`: the API hands each email to the
  mailing company to deliver, and sends the shop's API key with each
  request.
- `f4`, from `mailer` to `signup-api`: when an email can't be delivered
  (it bounces), the mailing company posts a bounce report (an email
  address) to `/hooks/bounce`, and the API takes that address off the
  list. The hook takes a report from any caller: the mailing company
  offers a signing secret for its reports, and the shop has not switched
  it on.

## Already in place

HTTPS everywhere. A load balancer in front of the API limits how many
requests one address can send. The hook can take an address off the list
and nothing else.

## The scales

Likelihood. 3: anyone on the internet could do it, with no account and
nothing stolen first. 2: it needs something first, such as a subscriber's
mailbox or a place inside the mailing company's systems. 1: it needs the
shop's own administrator rights.

Impact. 3: many subscribers are taken off the list, or the list of
addresses is exposed. 2: one subscriber is taken off the list. 1: a
nuisance, with nothing lost.
