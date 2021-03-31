# models.utilities.py
from datetime import datetime

from typing import Tuple


def return_adjusted_quarter_and_year(stmt_date: datetime, quarter_offset: int) -> Tuple[int, int]:

    q1_months = [1, 2, 3]
    q2_months = [4, 5, 6]
    q3_months = [7, 8, 9]
    q4_months = [10, 11, 12]

    # figure out the quarter and year
    quarter = 0

    if stmt_date.month in q1_months:
        quarter = 1
    elif stmt_date.month in q2_months:
        quarter = 2
    elif stmt_date.month in q3_months:
        quarter = 3
    elif stmt_date.month in q4_months:
        quarter = 4

    quarters = []
    years = []

    if quarter == 1:
        quarters.append(4)
        quarters.append(1)
        quarters.append(2)
        years.append(stmt_date.year - 1)
        years.append(stmt_date.year)
        years.append(stmt_date.year)
    elif quarter == 4:
        quarters.append(3)
        quarters.append(4)
        quarters.append(1)
        years.append(stmt_date.year)
        years.append(stmt_date.year)
        years.append(stmt_date.year + 1)
    else:
        quarters.append(quarter - 1)
        quarters.append(quarter)
        quarters.append(quarter + 1)
        years.append(stmt_date.year)
        years.append(stmt_date.year)
        years.append(stmt_date.year)

    return_quarter = quarters[quarter_offset + 1]
    return_year = years[quarter_offset + 1]

    return return_quarter, return_year
