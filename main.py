import datetime
from parser import categories, finance_report

categories.main()

# run finance reports on sunday
if datetime.datetime.now().weekday() == 0:
    finance_report.main()
