class Comment:
    def __init__(self):
        self.number = ""
        self.helpful = ""
        self.stars = ""
        self.header = ""
        self.comment = ""
    def printAll(self):
        print "\nNumber: %s\nHelpful: %s\nStars: %s\nHeader: %s\nComment:\n" %\
            (self.number, self.helpful, self.stars, self.header),
        for line in self.comment:
            print "%s" % line
    def getComment(self):
        return "".join(self.comment)
    def __repr__(self):
        return "\nNumber: %s\nHelpful: %s\nStars: %s\nHeader: %s\nComment: %s\n" %\
            (self.number, self.helpful, self.stars, self.header, \
            self.getComment())

