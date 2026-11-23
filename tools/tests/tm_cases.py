"""Threat models for test_tm_check.py: two stories, each with the reference
a lab's checks would hold and a model that is right for it, and the wrong
models of the first.

The first story is the shop's checkout, from Checkpoint 4 part 1's design
(docs/plans/cloud-module-4/, csa.m4.checkpoint.md): its designer's
reference, 64-line model and 25 wrong models, each aimed at one part of
tm-check. The second, a parcel company's drivers' app, is small and uses
what the first doesn't: abuse cases, "kept", "either" and a weakness that
may sit under either of two letters.
"""

# The models' lines are as long as a learner's are.
# ruff: noqa: E501

CHECKOUT_REF = {
    "elements": {
        "customer": ["external", "internet"],
        "staff": ["external", "office"],
        "psp": ["external", "provider"],
        "web": ["process", "edge"],
        "orders-api": ["process", "shop-net"],
        "backoffice": ["process", "shop-net"],
        "orders-db": ["store", "shop-net"],
        "app-logs": ["store", "shop-net"],
        "stock-db": ["store", "warehouse"],
    },
    "flows": {
        "f1": ["customer", "web"],
        "f2": ["customer", "psp"],
        "f3": ["web", "orders-api"],
        "f4": ["orders-api", "psp"],
        "f5": ["psp", "orders-api"],
        "f6": ["staff", "backoffice"],
        "f7": ["backoffice", "psp"],
        "f8": ["orders-api", "orders-db"],
        "f9": ["backoffice", "app-logs"],
        "f10": ["orders-api", "stock-db"],
    },
    # In this order: --only 1 is the staff sign-in, 2 the hook, 3 the
    # third-party script, 4 the key in the repository, 5 the logs, 6 the
    # refunds nobody signs.
    "weak": [
        {
            "flow": "f6",
            "letters": ["S"],
            "L": 3,
            "I": [3],
            "controls": ["mfa", "access-proxy", "mutual-tls"],
            "attack": ["T1110", "T1078"],
        },
        {
            "flow": "f5",
            "letters": ["S"],
            "L": 3,
            "I": [2],
            "controls": ["signing", "mutual-tls"],
        },
        {"flow": "f1", "letters": ["T"], "L": 2, "I": [3], "controls": ["integrity"]},
        {
            "flow": "f4",
            "letters": ["S", "I"],
            "L": 2,
            "I": [3],
            "controls": ["secret-store"],
            "attack": ["T1552"],
        },
        {
            "flow": "f9",
            "letters": ["I"],
            "L": 2,
            "I": [3],
            "controls": ["minimise-data"],
        },
        {"flow": "f6", "letters": ["R"], "L": 2, "I": [2], "controls": ["audit-log"]},
    ],
    "scope": {
        "web": "impacting",
        "orders-api": "cde",
        "backoffice": "cde",
        "orders-db": "cde",
        "app-logs": "cde",
        "stock-db": "out",
    },
}

CHECKOUT_MODEL = """\
# The shop's checkout: threat model.
zone internet   anyone on the internet
zone office     the shop's office network, staff laptops
zone provider   the payment provider, PayPoint
zone edge       the shop's storefront on the cloud's CDN
zone shop-net   the shop's cloud subnet 10.20.1.0/24
zone warehouse  the warehouse network 10.30.0.0/24

element customer   external internet   a customer's browser
element staff      external office     a staff member's laptop
element psp        external provider   PayPoint's card form and API
element web        process  edge       storefront and checkout page
element orders-api process  shop-net   orders, payments and refunds
element backoffice process  shop-net   staff pages: refunds, phone orders
element orders-db  store    shop-net   orders, last four digits, provider tokens
element app-logs   store    shop-net   the log server
element stock-db   store    warehouse  stock levels

flow f1  customer   web        browse and open the checkout page
flow f2  customer   psp        the card form posts the card to PayPoint
flow f3  web        orders-api create an order
flow f4  orders-api psp        create a payment, refund one
flow f5  psp        orders-api the payment-result hook
flow f6  staff      backoffice sign in, refunds, phone orders
flow f7  backoffice psp        a phone order's card number
flow f8  orders-api orders-db  read and write orders
flow f9  backoffice app-logs   request logs
flow f10 orders-api stock-db   reserve stock

scope web        impacting it serves the page that holds the provider's card form
scope orders-api cde no card data, but it shares an unfiltered subnet with backoffice
scope backoffice cde phone orders send card numbers through it
scope orders-db  cde same unfiltered subnet as backoffice, though it stores no card numbers
scope app-logs   cde request logs hold card numbers and codes today
scope stock-db   out firewalled, receives no card data and opens no connections back

threat t1 f6 S 3 3 9 An attacker on the internet can sign in to the back office with a guessed or stolen staff password and refund money to a card of their own
threat t2 f5 S 3 2 6 An attacker can post a forged payment result to the hook so that an unpaid order is sent out
threat t3 f1 T 2 3 6 An attacker who controls the analytics company's script can change the checkout page to show a card form of their own and collect card numbers
threat t4 f4 I 2 3 6 A contractor who can read the repository can take the provider API key from it and pay refunds out of the shop's account
threat t5 f9 I 2 3 6 An engineer who can read the log server can collect the card numbers and codes that phone orders leave in the request logs
threat t6 f6 R 2 2 4 A staff member can deny making a refund because the back office records refunds without the name of who made them

none f1 SRIDE the page is served over HTTPS from the CDN, which absorbs floods; it takes no sign-in
none f2 STRIDE the card goes straight to the provider over HTTPS and the provider protects its own form
none f3 STRIDE order requests carry no card data and the API checks every field and rate-limits
none f4 STRD the provider's API is authenticated both ways over HTTPS and logs every call
none f4 E the key can only create and refund payments for this shop
none f5 TRIDE the hook only reads a payment id and a status and looks nothing else up
none f6 TID HTTPS with a role check on every page behind the load balancer's rate limit
none f6 E every page checks the staff role of the signed-in person
none f7 STRIDE the back office calls the provider's API over HTTPS with its own restricted key
none f10 STRIDE a firewall lets only the orders API reach the stock port and every query is logged

control c1 t1 mfa every back-office sign-in needs a security key as well as the password
control c2 t2 signing check PayPoint's signature on every hook request with the signing secret
control c3 t3 integrity pin the script with a hash and allow only listed script sources
control c4 t4 secret-store move the key to the cloud's secrets manager, rotate it, and scan pushes
control c5 t5 minimise-data never log request bodies of the phone-order page; remove the old logs
control c6 t6 audit-log record every refund with the staff member, time, order and amount

top t1 t2 t3 t4 t5
attack t1 T1110.004
attack t4 T1552.001

goal g1 t1 refund money to the attacker's own card
node n1 g1 or get into the back office
node n2 n1 and phish a staff member
leaf l1 n2 200 send a convincing sign-in page to ten staff
leaf l2 n2 50 use the captured password before it is changed
leaf l3 n1 100 try leaked passwords against the sign-in page
leaf l4 n1 2000 bribe a staff member
cheapest g1 100
"""


def change(old: str, new: str, text: str = CHECKOUT_MODEL) -> str:
    """The model with one piece of text replaced; the piece must be there."""
    assert old in text, old
    return text.replace(old, new, 1)


T2 = "threat t2 f5 S 3 2 6 An attacker can post a forged payment result to the hook so that an unpaid order is sent out\n"
C2 = "control c2 t2 signing check PayPoint's signature on every hook request with the signing secret\n"
C3 = "control c3 t3 integrity pin the script with a hash and allow only listed script sources\n"
T5_WORDS = "An engineer who can read the log server can collect the card numbers and codes that phone orders leave in the request logs"
T4_WORDS = "A contractor who can read the repository can take the provider API key from it and pay refunds out of the shop's account"

# name: (the wrong model, the one part it fails, what tm-check says)
CHECKOUT_WRONG = {
    # the diagram
    "psp-inside": (
        change(
            "element psp        external provider",
            "element psp        external shop-net",
        ),
        "boundaries",
        "two parts that different people run, or that sit on different networks, share a zone",
    ),
    "one-big-zone": (
        change(
            "element web        process  edge", "element web        process  shop-net"
        ),
        "boundaries",
        "two parts that different people run, or that sit on different networks, share a zone",
    ),
    "logs-as-process": (
        change("element app-logs   store ", "element app-logs   process"),
        "diagram",
        "a part of the design is drawn as the wrong kind of element",
    ),
    "hook-backwards": (
        change("flow f5  psp        orders-api", "flow f5  orders-api psp       "),
        "diagram",
        "a flow doesn't run from the side that starts it to the side that answers",
    ),
    # STRIDE
    "missing-letter": (
        change(
            "none f6 E every page checks the staff role of the signed-in person\n", ""
        ),
        "stride",
        "a flow that crosses a boundary hasn't been reviewed for all six letters",
    ),
    "none-where-weak": (
        change(
            "top t1 t2 t3",
            "top t1 t3",
            change(C2, "", change("none f5 TRIDE", "none f5 STRIDE", change(T2, ""))),
        ),
        "findings",
        "something the design describes as weak is marked as nothing to record",
    ),
    "boilerplate": (
        change(T5_WORDS, T4_WORDS),
        "stride",
        "two threats read the same once the names are taken out",
    ),
    # ratings
    "logs-rated-low": (
        change(
            "top t1 t2 t3 t4 t5",
            "top t1 t2 t3 t4",
            change("threat t5 f9 I 2 3 6", "threat t5 f9 I 1 3 3"),
        ),
        "findings",
        "a threat's likelihood or impact isn't what the design's scales give it",
    ),
    "script-rated-anyone": (
        change(
            "top t1 t2 t3 t4 t5",
            "top t1 t3 t2 t4 t5",
            change("threat t3 f1 T 2 3 6", "threat t3 f1 T 3 3 9"),
        ),
        "findings",
        "a threat's likelihood or impact isn't what the design's scales give it",
    ),
    "risk-sum": (
        change(
            "top t1 t2 t3 t4 t5",
            "top t1 t3 t4 t5",
            change("threat t2 f5 S 3 2 6", "threat t2 f5 S 3 2 5"),
        ),
        "ranking",
        "line 38: the risk says 5, and likelihood 3 times impact 2 is 6",
    ),
    "top-unordered": (
        change("top t1 t2 t3 t4 t5", "top t2 t1 t3 t4 t5"),
        "ranking",
        "the top line isn't in order, highest risk first",
    ),
    # controls
    "tls-for-the-hook": (
        change("control c2 t2 signing", "control c2 t2 tls"),
        "controls",
        "a control is of a kind that doesn't answer its threat",
    ),
    "encrypt-the-logs": (
        change("control c5 t5 minimise-data", "control c5 t5 encryption"),
        "controls",
        "a control is of a kind that doesn't answer its threat",
    ),
    "password-rules-for-sign-in": (
        change("control c1 t1 mfa", "control c1 t1 authn"),
        "controls",
        "a control is of a kind that doesn't answer its threat",
    ),
    "key-stays-in-repo-encrypted": (
        change("control c4 t4 secret-store", "control c4 t4 encryption"),
        "controls",
        "a control is of a kind that doesn't answer its threat",
    ),
    "accept-a-high": (
        change(C3, "accept t3 the analytics company is reputable\n"),
        "controls",
        "a risk of 6 or more is accepted",
    ),
    # PCI DSS scope
    "web-out-of-scope": (
        change(
            "scope web        impacting it serves",
            "scope web        out it never sees a card number and only serves",
        ),
        "scope",
        "something that card data reaches, or that could change what happens to it, is marked out of scope",
    ),
    "only-backoffice-in-scope": (
        change(
            "scope orders-db  cde same unfiltered subnet as backoffice, though it stores no card numbers",
            "scope orders-db  out it stores only last four digits and tokens",
            change(
                "scope orders-api cde no card data, but it shares an unfiltered subnet with backoffice",
                "scope orders-api out it never sees a card number at all",
            ),
        ),
        "scope",
        "something that card data reaches, or that could change what happens to it, is marked out of scope",
    ),
    "logs-out-of-scope": (
        change(
            "scope app-logs   cde request logs hold card numbers and codes today",
            "scope app-logs   out a log server is not a payment system",
        ),
        "scope",
        "something that card data reaches, or that could change what happens to it, is marked out of scope",
    ),
    "everything-in-scope": (
        change(
            "scope stock-db   out firewalled, receives no card data and opens no connections back",
            "scope stock-db   cde to be on the safe side everything is in scope",
        ),
        "scope",
        "something the design keeps apart from card data is marked in scope",
    ),
    "web-called-cde": (
        change("scope web        impacting", "scope web        cde"),
        "scope",
        "an in-scope part has the wrong reason for being in scope (cde or impacting)",
    ),
    "customer-scoped": (
        change(
            "scope stock-db   out",
            "scope customer out the customer's browser is theirs not ours here\nscope stock-db   out",
        ),
        "scope",
        "a scope line names something the business doesn't run",
    ),
    # ATT&CK and the tree
    "attack-wrong": (
        change("attack t4 T1552.001", "attack t4 T1110"),
        "attack",
        "a threat the task asks an ATT&CK technique for has none that fits it",
    ),
    "tree-sum": (
        change("cheapest g1 100", "cheapest g1 250"),
        "tree",
        "the cheapest line isn't the cheapest path through the tree",
    ),
    "tree-flat": (
        change(
            "cheapest g1 100",
            "cheapest g1 50",
            change(
                "leaf l2 n2",
                "leaf l2 n1",
                change(
                    "leaf l1 n2",
                    "leaf l1 n1",
                    change("node n2 n1 and phish a staff member\n", ""),
                ),
            ),
        ),
        "tree",
        "the attack tree needs at least three leaves and an and node with two steps",
    ),
}

# Which "controls --only N" each wrong control fails (N counts the
# reference's weaknesses from 1), and whether "--only rest" fails too.
CHECKOUT_ONLY = {
    "password-rules-for-sign-in": (1, False),
    "tls-for-the-hook": (2, False),
    "accept-a-high": (3, True),
    "key-stays-in-repo-encrypted": (4, False),
    "encrypt-the-logs": (5, False),
}

# --- the second story: a parcel company's drivers' app ----------------------

PARCELS_REF = {
    "elements": {
        "driver": ["external", "internet"],
        "app": ["process", "depot"],
        "parcels-db": ["store", "depot"],
        "maps": ["external", "maps-co"],
    },
    "flows": {
        "f1": ["driver", "app"],
        "f2": ["app", "parcels-db"],
        "f3": ["maps", "app"],
    },
    "weak": [
        {"flow": "f1", "letters": ["S"], "L": 3, "I": 3, "controls": ["mfa"]},
        # The made-up road closure: spoofing or tampering, either is a fair
        # reading.
        {"flow": "f3", "letters": ["S", "T"], "L": 3, "I": [2, 3]},
    ],
    # The database is the cloud's managed service: one zone with the app or
    # its own, the design leaves open.
    "either": [["app", "parcels-db"]],
    "kept": {"t1": "f1", "t2": "f3"},
}

PARCELS_MODEL = """\
zone internet anyone on the internet
zone depot Riverside's cloud network
zone maps-co the maps company
element driver external internet a driver's phone
element app process depot the drivers' API
element parcels-db store depot parcels and doorstep photos
element maps external maps-co the maps company's servers
flow f1 driver app sign in and update a delivery
flow f2 app parcels-db read and write parcels
flow f3 maps app road-closure reports
threat t1 f1 S 3 3 9 An attacker on the internet can sign in as a driver with a phished password and redirect parcels
threat t2 f3 S 3 2 6 An attacker can post a made-up road closure to the hook so that drivers are sent the long way round
threat t3 f1 R 2 1 2 A driver can deny marking a parcel delivered because the app keeps no record of who did
none f1 TIDE HTTPS, a role check on every request and the load balancer's rate limit
none f3 TRIDE the hook reads a road name and a time and looks nothing else up
control c1 t1 mfa a code from the driver's phone as well as the password
control c2 t2 signing check the maps company's signature on every report
accept t3 a wrong delivery mark is settled with the photo
top t1 t2
attack t1 T1078
goal g1 t1 redirect a parcel
node n1 g1 or get a driver's session
node n2 n1 and phish a driver
leaf l1 n2 100 send a fake sign-in page
leaf l2 n2 20 use the password the same day
leaf l3 n1 500 bribe a driver
cheapest g1 120
abuse a1 t1 As an attacker, I sign in with a phished password so that I can redirect parcels
test x1 a1 sign in with a known password and no code, and expect a refusal
abuse a2 t2 As a rival, I post made-up closures so that deliveries run late
test x2 a2 post an unsigned report and expect it to be refused
"""
