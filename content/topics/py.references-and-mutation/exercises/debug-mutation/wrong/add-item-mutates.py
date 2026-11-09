def add_item(items, item):
    """Return a new list with the item added; the list given is unchanged."""
    items.append(item)
    return items


def main():
    shopping = ["milk"]
    backup = list(shopping)
    longer = add_item(shopping, "eggs")
    shopping.append("tea")
    print(shopping)
    print(longer)
    print(backup)


main()
