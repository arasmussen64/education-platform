def initials(full_name):
    result = full_name[0]
    position = 1
    while position < len(full_name):
        if full_name[position - 1] == " ":
            result = result + full_name[position]
        position += 1
    return result
