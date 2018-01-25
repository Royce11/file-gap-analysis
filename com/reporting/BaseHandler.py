class BaseHandler:

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def getStartDate(self):
        return self.start_date

    def getEndDate(self):
        return  self.end_date