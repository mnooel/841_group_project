# models.income_statement.py

import pandas as pd
from datetime import datetime

from models.utilities import return_adjusted_quarter_and_year


def return_quarterly_is_df(ticker: str) -> pd.DataFrame:
    path = f'fin_data_input/{ticker}_quarterly_financials.csv'
    df = pd.read_csv(path)

    # drop unwanted ttm column
    df = df.drop(['ttm'], axis=1)
    # replace unwanted strings parts and fill na
    df['name'] = df['name'].str.replace('\t', '')
    df = df.replace(',', '', regex=True)
    df = df.fillna(0)

    # set the index to the column name
    df = df.set_index('name')

    # convert column values to floats
    for column in df.columns:
        df[column] = df[column].astype(float)

    return df


def convert_is_df_to_records_dict(df: pd.DataFrame) -> dict:
    # transpose the dataframe
    df = df.transpose()

    # reset the index to the statement date and infer datetime
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'StatementDate'}, inplace=True)
    df['StatementDate'] = pd.to_datetime(df['StatementDate'], format='%m/%d/%Y')

    # return dict of records
    records = df.to_dict(orient='records')

    return records


class IncomeStatement:

    def __init__(self, ticker: str, quarter_offset: int, **kwargs):
        # company and date info
        self.ticker: str = ticker
        self.statement_date: datetime = kwargs['StatementDate']
        quarter, year = return_adjusted_quarter_and_year(stmt_date=self.statement_date, quarter_offset=quarter_offset)
        self.quarter: int = quarter
        self.year: int = year

        # gross profit
        self.gross_profit: float = kwargs['GrossProfit']
        self.cogs: float = kwargs['CostOfRevenue'] * -1
        self.revenue: float = self.gross_profit - self.cogs

        # operating expenses
        self.operating_income: float = kwargs['OperatingIncome']
        self.selling_general_and_admin: float = kwargs['SellingGeneralAndAdministration'] * -1
        self.research_and_development: float = kwargs['ResearchAndDevelopment'] * -1
        total_operating_expenses: float = self.operating_income - self.gross_profit
        self.operating_expenses: float = \
            total_operating_expenses - self.selling_general_and_admin - self.research_and_development

        # other income and expenses
        self.pretax_income: float = kwargs['PretaxIncome']
        total_other_exp: float = self.pretax_income - self.operating_income
        self.net_interest_exp: float = kwargs['NetInterestIncome']
        self.net_other_exp: float = total_other_exp - self.net_interest_exp

        # taxes and net income
        self.net_income: float = kwargs['NetIncome']
        self.taxes: float = self.pretax_income - self.net_income
        if self.pretax_income == 0:
            self.tax_rate: float = 0
        else:
            self.tax_rate: float = self.taxes / self.pretax_income
        self.nopat: float = self.operating_income * (1 - self.tax_rate)

        # other values
        self.interest_exp: float = kwargs['InterestExpense']
        self.ebit: float = kwargs['EBIT']
        self.dep_and_amort: float = kwargs['ReconciledDepreciation']
        self.ebitda: float = self.ebit + self.dep_and_amort
        if 'PreferredStockDividends' not in kwargs:
            self.ps_div: float = 0.0
        else:
            self.ps_div: float = kwargs['PreferredStockDividends']
        self.eps_diluted: float = kwargs['DilutedEPS']

    def __repr__(self):
        return f'{self.__class__.__name__}: {self.ticker} Q{self.quarter} {self.year}'

    def print_income_statement(self):
        print_string = ''
        items_to_print = [
            'revenue', 'cogs', 'gross_profit', 'selling_general_and_admin', 'research_and_development',
            'operating_expenses', 'operating_income', 'net_interest_exp', 'net_other_exp', 'pretax_income',
            'taxes', 'net_income'
        ]

        for item in items_to_print:
            print_string += f'{item}'.ljust(25)
            print_string += f'{"{:,}".format(getattr(self, item))}\n'.rjust(20)

        print(print_string)

    def return_data_list(self) -> list:

        return_list = [
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '1 - Gross Profit',
             'account': '1.1 - Revenue',
             'amount': self.revenue
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '1 - Gross Profit',
             'account': '1.2 - COGS',
             'amount': self.cogs
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '2 - Operating Expenses',
             'account': '2.1 - SG&A',
             'amount': self.selling_general_and_admin
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '2 - Operating Expenses',
             'account': '2.2 - R&D',
             'amount': self.research_and_development
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '2 - Operating Expenses',
             'account': '2.3 - Operating Expenses',
             'amount': self.operating_expenses
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '3 - Other Income/Expenses',
             'account': '3.1 - Net Interest Expense',
             'amount': self.net_interest_exp
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '3 - Other Income/Expenses',
             'account': '3.2 - Net Other Expenses',
             'amount': self.net_other_exp
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '4 - Taxes',
             'account': '4.1 - Taxes',
             'amount': self.taxes
             },
        ]

        return return_list

    def add_other_income_statement(self, **kwargs):
        attributes_to_ignore: list = [
            'ticker', 'statement_date', 'quarter', 'year'
        ]
        for attribute in list(kwargs.keys()):
            if attribute not in attributes_to_ignore:
                new_value = getattr(self, attribute) + kwargs[attribute]
                setattr(self, attribute, new_value)


def combine_income_statements_to_dict(*args: IncomeStatement):

    dates = [inc_stmt.statement_date for inc_stmt in args]

    gross_profit = sum([inc_stmt.gross_profit for inc_stmt in args])
    cogs = sum([inc_stmt.cogs for inc_stmt in args])
    op_inc = sum([inc_stmt.operating_income for inc_stmt in args])
    sga = sum([inc_stmt.selling_general_and_admin for inc_stmt in args])
    rad = sum([inc_stmt.research_and_development for inc_stmt in args])
    pretax_inc = sum([inc_stmt.pretax_income for inc_stmt in args])
    net_int_exp = sum([inc_stmt.net_interest_exp for inc_stmt in args])
    net_income = sum([inc_stmt.net_income for inc_stmt in args])
    int_exp = sum([inc_stmt.interest_exp for inc_stmt in args])
    ebit = sum([inc_stmt.ebit for inc_stmt in args])
    rec_dep = sum([inc_stmt.dep_and_amort for inc_stmt in args])
    ps_div = sum([inc_stmt.ps_div for inc_stmt in args])
    diluted_eps = sum([inc_stmt.eps_diluted for inc_stmt in args])

    return_dict = {
        'StatementDate': max(dates),
        'GrossProfit': gross_profit,
        'CostOfRevenue': cogs * -1,
        'OperatingIncome': op_inc,
        'SellingGeneralAndAdministration': sga * -1,
        'ResearchAndDevelopment': rad * -1,
        'PretaxIncome': pretax_inc,
        'NetInterestIncome': net_int_exp,
        'NetIncome': net_income,
        'InterestExpense': int_exp,
        'EBIT': ebit,
        'ReconciledDepreciation': rec_dep,
        'PreferredStockDividends': ps_div,
        'DilutedEPS': diluted_eps
    }

    return return_dict
