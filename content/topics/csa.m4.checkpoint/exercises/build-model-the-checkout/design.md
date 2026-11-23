# The shop: the checkout and card payments

The shop is adding card payments to its website through a payment
provider, PayPoint. This note describes the design as it stands, before
its security review.

## The parts

- `customer`: a customer's browser, anywhere on the internet.
- `staff`: a staff member's laptop, on the shop's office network.
- `psp`: PayPoint, the payment provider: its card form and its API.
  PayPoint runs both, and is assessed against PCI DSS itself.
- `web`: the storefront and the checkout page. They are static files on
  the cloud's object storage, served through the cloud's CDN, with no
  route into the shop's subnet. The checkout page shows PayPoint's card
  form in an inline frame, so a card number goes from the customer's
  browser straight to PayPoint. The page also loads `stats.js` from an
  analytics company's server, by its address. Nothing pins what that file
  holds, and the page's headers allow scripts from anywhere.
- `orders-api`: creates orders, asks PayPoint to take each payment, and
  makes refunds. It never receives a card number. Its PayPoint API key,
  which can make refunds, is in `config/prod.env` in its repository,
  which every contractor can read. Its hook, `/hooks/payment`, takes
  PayPoint's "paid" message from any caller: PayPoint signs each message,
  and checking the signature is not switched on. A "paid" message marks
  the order for dispatch.
- `backoffice`: the staff pages, for refunds and phone orders. Its address
  is public, and staff sign in with a password. For a phone order, a
  member of staff types the customer's card number, expiry date and
  security code into a form, and the back office sends them to PayPoint.
  It logs the body of every request it receives. Refunds are recorded
  with the order and the amount, and not with who made them. Every page
  checks that the signed-in person has the staff role.
- `orders-db`: the orders, the last four digits of each card, and
  PayPoint's token for each payment.
- `app-logs`: the log server. Every engineer can read it.
- `stock-db`: the stock levels, on the warehouse network. A firewall lets
  only `orders-api` open connections to its database port. Nothing on the
  warehouse network can open a connection to the shop's subnet, and no
  card data is sent there.

## The networks

`orders-api`, `backoffice`, `orders-db` and `app-logs` are on one subnet
in the shop's cloud, 10.20.1.0/24, with nothing filtering between them.
The shop runs all four.

## The flows

- `f1`, from `customer` to `web`: browsing, and opening the checkout page.
- `f2`, from `customer` to `psp`: the card form sends the card to PayPoint.
- `f3`, from `web` to `orders-api`: the checkout page creates an order.
- `f4`, from `orders-api` to `psp`: a payment is taken, or a refund made.
- `f5`, from `psp` to `orders-api`: PayPoint's "paid" message, to the hook.
- `f6`, from `staff` to `backoffice`: sign-in, refunds and phone orders.
- `f7`, from `backoffice` to `psp`: a phone order's card details.
- `f8`, from `orders-api` to `orders-db`: orders read and written.
- `f9`, from `backoffice` to `app-logs`: the request logs.
- `f10`, from `orders-api` to `stock-db`: stock reserved for an order.

## Already in place

HTTPS everywhere. The CDN absorbs floods. The load balancer in front of
the shop's subnet limits how many requests one address can send.
PayPoint's API authenticates both ways.

## The scales

Likelihood. 3: anyone on the internet could do it, with no account and
nothing stolen first. 2: it needs something first, such as a staff
member's or a contractor's account, or control of a supplier's or the
shop's own system. 1: it needs an administrator's rights, or someone
standing at the machine.

Impact. 3: card numbers are exposed, or money is paid out of the shop's
account. 2: an order or one customer's details are exposed or falsified
(goods sent without being paid for count here), or the record of who did
something is missing. 1: a nuisance, with nothing lost.
