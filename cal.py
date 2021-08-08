import calendar
import datetime
from dateutil import relativedelta


class Date_with_past(datetime.date):

    past = False
    zero = False


class Calendar(calendar.Calendar):

    today = datetime.date.today()
    next_month = today + relativedelta.relativedelta(months=1)

    def __init__(self, year=today.year, month=today.month, next=False):
        super().__init__(firstweekday=6)
        if next:
            self.year = self.next_month.year
            self.month = self.next_month.month
        else:
            self.year = year
            self.month = month

        self.day_names = ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")
        self.months = (
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        )

    def get_days(self):
        weeks = self.monthdays2calendar(self.year, self.month)
        days = []
        for week in weeks:
            for day, _ in week:
                if day == 0:
                    day_obj = Date_with_past(self.year, self.month, 1)
                    day_obj.zero = True
                else:
                    day_obj = Date_with_past(self.year, self.month, day)
                    if (
                        self.year == self.today.year
                        and self.month == self.today.month
                        and day <= self.today.day
                    ):
                        day_obj.past = True
                days.append(day_obj)
        return days

    def get_month(self):
        return self.months[self.month - 1]
