def unique_in_order(emails):
    """The distinct emails, in the order they first appear."""
    seen = []
    result = []
    for email in emails:
        if email not in seen:
            seen.append(email)
            result.append(email)
    return result


emails = [f"user{i % 1500}@example.com" for i in range(3000)]
unique = unique_in_order(emails)
print(len(unique), unique[:2], unique[-1])
