def add_item(items, item):
    """Return a new list with the item added; the list given is unchanged."""
    result = list(items)
    result.append(item)
    return result


def main():
    shopping = ["milk"]
    backup = shopping
    longer = add_item(shopping, "eggs")
    shopping.append("tea")
    print(shopping)
    print(longer)
    print(backup)


main()
