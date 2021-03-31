# render_ratio_data.py

import pandas as pd
import itertools

from models.company import Company
from settings import COMPANIES_LIST


def render_ratio_data():

    companies = [Company(**company) for company in COMPANIES_LIST]

    ratio_data = []

    for company in companies:
        for year in company.statement_groups:
            consolidated_statement = company.statement_groups[year]
            ratio_data.append(consolidated_statement.return_data_list())

    flat_list = list(itertools.chain(*ratio_data))

    ratio_df = pd.DataFrame(flat_list)

    ratio_df.to_csv('fin_data_output/ratio_data.csv', index=False)


if __name__ == '__main__':
    render_ratio_data()
