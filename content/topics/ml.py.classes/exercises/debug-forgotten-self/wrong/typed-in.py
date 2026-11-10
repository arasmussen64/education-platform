class Player:
    def __init__(self, name):
        self.name = name
        self.score = 30

    def add_points(self, points):
        pass

    def __repr__(self):
        return f"Player({self.name!r}, {self.score})"


ada = Player("Ada")
print(ada)
print(ada.score)
