class Player:
    def __init__(self, name):
        self.name = name
        score = 0

    def add_points(self, points):
        self.score = self.score + points

    def __repr__(self):
        return f"Player({self.name!r}, {self.score})"


ada = Player("Ada")
ada.add_points(10)
ada.add_points(20)
print(ada)
print(ada.score)
