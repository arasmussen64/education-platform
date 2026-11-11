"""Read-only price lookups from the public Azure Retail Prices API.

No sign-in, no subscription: https://prices.azure.com/api/retail/prices is a
public endpoint. Prints pay-as-you-go (Consumption) prices in USD.

    python azure_prices.py vm eastus2 Standard_B2s Standard_B2ms ...
    python azure_prices.py service "Azure Bastion" eastus2
    python azure_prices.py filter "<raw OData filter>"
"""

import json
import sys
import urllib.parse
import urllib.request

API = "https://prices.azure.com/api/retail/prices"


def fetch(odata_filter: str) -> list[dict]:
    url = API + "?" + urllib.parse.urlencode({"$filter": odata_filter})
    items: list[dict] = []
    while url:
        with urllib.request.urlopen(url, timeout=60) as response:
            page = json.load(response)
        items += page["Items"]
        url = page.get("NextPageLink")
    return items


def show(items: list[dict]) -> None:
    for item in sorted(
        items, key=lambda i: (i["armRegionName"], i["productName"], i["skuName"], i["meterName"])
    ):
        print(
            f"{item['armRegionName']:14} {item['retailPrice']:>10.5f} {item['unitOfMeasure']:14} "
            f"{item['productName']} | {item['skuName']} | {item['meterName']} | {item.get('armSkuName', '')}"
        )


def main() -> None:
    kind = sys.argv[1]
    if kind == "vm":
        region, *skus = sys.argv[2:]
        for sku in skus:
            items = fetch(
                "serviceName eq 'Virtual Machines' and priceType eq 'Consumption' "
                f"and armRegionName eq '{region}' and armSkuName eq '{sku}'"
            )
            # Leave out Spot and Low Priority, which can be evicted mid-lab.
            show([i for i in items if "Spot" not in i["skuName"] and "Low Priority" not in i["skuName"]])
    elif kind == "service":
        service, region = sys.argv[2:4]
        show(
            fetch(
                f"serviceName eq '{service}' and priceType eq 'Consumption' and armRegionName eq '{region}'"
            )
        )
    elif kind == "filter":
        show(fetch(sys.argv[2]))


if __name__ == "__main__":
    main()
