# render_bs_data.py

import pandas as pd
import itertools

from models.company import Company
from settings import COMPANIES_LIST


def render_bs_data():

    companies = [Company(**company) for company in COMPANIES_LIST]

    bs_data = list(itertools.chain(*[company.return_bs_data_list() for company in companies]))

    is_df = pd.DataFrame(bs_data)

    is_df.to_csv('fin_data_output/bs_data.csv', index=False)


if __name__ == '__main__':
    render_bs_data()
