# render_is_data.py

import pandas as pd
import itertools

from models.company import Company
from settings import COMPANIES_LIST


def render_is_data():

    companies = [Company(**company) for company in COMPANIES_LIST]

    is_data = list(itertools.chain(*[company.return_is_data_list() for company in companies]))

    is_df = pd.DataFrame(is_data)

    is_df.to_csv('fin_data_output/is_data.csv', index=False)


if __name__ == '__main__':
    render_is_data()
