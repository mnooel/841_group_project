# models.cashflow_statement.py

import pandas as pd

from models.utilities import return_adjusted_quarter_and_year


def return_quarterly_cf_df(ticker: str) -> pd.DataFrame:
    path = f'fin_data_input/{ticker}_quarterly_cash-flow.csv'

    df = pd.read_csv(path)

    # drop unwanted ttm column
    df = df.drop(['ttm'], axis=1)
    # remove unwanted string types and convert to numeric
    df['name'] = df['name'].str.replace('\t', '')
    df = df.replace(',', '', regex=True)
    df = df.fillna(0)

    # set the index to the column name
    df = df.set_index('name')

    # convert to floats
    for column in df.columns:
        df[column] = df[column].astype(float)

    return df


def convert_cf_df_to_records_dict(df: pd.DataFrame) -> dict:
    # transpose the dataframe
    df = df.transpose()

    # reset the index to the statement date and infer datetime
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'StatementDate'}, inplace=True)
    df['StatementDate'] = pd.to_datetime(df['StatementDate'], format='%m/%d/%Y')

    # return dict of records
    records = df.to_dict(orient='records')

    return records


class CashFlowStatement:

    def __init__(self, ticker: str, quarter_offset: int, **kwargs):
        # company and date info
        self.ticker: str = ticker
        self.statement_date = kwargs['StatementDate']
        quarter, year = return_adjusted_quarter_and_year(self.statement_date, quarter_offset)
        self.quarter: int = quarter
        self.year: int = year

        # capital expenditures
        self.capex: float = kwargs['CapitalExpenditure']

    def __repr__(self):
        return f'{self.ticker}: {self.quarter}-{self.year}'


def combine_cash_flow_statements_to_dict(*args: CashFlowStatement):

    dates = [cfs.statement_date for cfs in args]

    capex = sum([cfs.capex for cfs in args])

    return_dict = {
        'StatementDate': max(dates),
        'CapitalExpenditure': capex
    }

    return return_dict
