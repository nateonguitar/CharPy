class Vector2():

    def __init__(self, x, y):
        self.x = x
        self.y = y


    def clone(self):
        return Vector2(self.x, self.y)


    @staticmethod
    def zero():
        return Vector2(x=0, y=0)


    def __str__(self):
        return f'({self.x},{self.y})'