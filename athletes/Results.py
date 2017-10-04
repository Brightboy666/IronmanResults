class Division(object):
    def __init__(self, male:bool, lowAge:int, highAge:int):
        self.male = male
        self.lowAge = lowAge
        self.highAge = highAge

    def toAGStr(self):
        sex = "M" if self.male else "F"
        divStr = "{}{}-{}".format(sex, self.lowAge, self.highAge)
        return divStr