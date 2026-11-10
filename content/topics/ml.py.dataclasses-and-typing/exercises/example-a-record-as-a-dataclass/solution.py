from dataclasses import dataclass


@dataclass
class Book:
    title: str
    pages: int
    price: float = 0.0


dune = Book("Dune", 412, 9.99)
hobbit = Book("The Hobbit", 310)
print(dune)
print(hobbit)
print(dune == Book("Dune", 412, 9.99))


def total_pages(books: list[Book]) -> int:
    total = 0
    for book in books:
        total = total + book.pages
    return total


print(total_pages([dune, hobbit]))
