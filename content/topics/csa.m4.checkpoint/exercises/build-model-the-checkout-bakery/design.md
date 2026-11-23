# Hartley's Bakery: online orders

Hartley's Bakery takes orders for cakes on its own website, and takes the
card on its own form. Customers can save a card for their next order.
This note describes the design as it stands, before its security review.

## The parts

- `customer`: a customer's browser, anywhere on the internet. A customer
  signs up for an account, free, to order.
- `developer`: a developer's laptop, at home. The bakery's two developers
  answer customers' questions about their orders.
- `psp`: CardWorks, the payment provider: its payment API. CardWorks runs
  it, and is assessed against PCI DSS itself.
- `shopfront`: the bakery's pages and its own card form. The customer
  types the card number, expiry date and security code into the form, and
  the page sends them, with the order, to `orders`. The order form also
  sends each cake's price. The admin pages, where the owner downloads the
  saved cards' details for refunds, are pages of `shopfront` too, and
  check only that someone is signed in. The bakery's old address,
  `http://`, with no TLS, still serves the whole site, card form included,
  as the new `https://` address does.
- `orders`: takes each order, charges the card through CardWorks for the
  price the order carries, and saves the card number for repeat orders.
- `cards-db`: the saved card numbers, as they were typed, with each
  customer's name. Developers query it with their own database accounts,
  from home, over TLS, to answer questions; the database keeps no record
  of the queries.
- `bake-list`: the kitchen's print server, on the kitchen network. A
  firewall lets only `orders` open connections to it, and nothing on the
  kitchen network can open a connection to the bakery's cloud subnet.
  It receives how many of each loaf and cake to bake, and no card data.

## The networks

`shopfront`, `orders` and `cards-db` are on one subnet in the bakery's
cloud, with nothing filtering between them.

## The flows

- `f1`, from `customer` to `shopfront`: browsing, signing in, ordering and
  paying on the card form.
- `f2`, from `shopfront` to `orders`: the order, with its card number.
- `f3`, from `orders` to `psp`: the card charged.
- `f4`, from `orders` to `cards-db`: the card saved for repeat orders.
- `f5`, from `orders` to `bake-list`: the day's loaves and cakes.
- `f6`, from `developer` to `cards-db`: questions answered from the database.

## Already in place

HTTPS on the new address. The load balancer limits how many requests one
address can send. CardWorks' API authenticates both ways and logs every
charge. Orders are recorded with the customer's account.

## The scales

Likelihood. 3: anyone on the internet could do it, with no account and
nothing stolen first, or with an account anyone can make. 2: it needs
something first, such as a developer's account, a place on the customer's
own network, or control of one of the bakery's systems. 1: it needs an
administrator's rights, or someone standing at the machine.

Impact. 3: card numbers are exposed, or money is paid out of the bakery's
account. 2: an order, or one customer's details, is exposed or falsified
(a cake sold for less than its price counts here), or the record of who
did something is missing. 1: a nuisance, with nothing lost.
