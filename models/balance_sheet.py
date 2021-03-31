# models.balance_sheet.py

import pandas as pd

from models.utilities import return_adjusted_quarter_and_year


def return_quarterly_bs_df(ticker: str) -> pd.DataFrame:
    path = f'fin_data_input/{ticker}_quarterly_balance-sheet.csv'
    df = pd.read_csv(path)

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


def convert_bs_df_to_records_dict(df: pd.DataFrame) -> dict:
    # transpose the dataframe
    df = df.transpose()

    # reset the index to the statement date and infer datetime
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'StatementDate'}, inplace=True)
    df['StatementDate'] = pd.to_datetime(df['StatementDate'], format='%m/%d/%Y')

    # return dict of records
    records = df.to_dict(orient='records')

    return records


class BalanceSheet:

    def __init__(self, ticker: str, quarter_offset: int, **kwargs):
        # company and date info
        self.ticker: str = ticker
        self.statement_date = kwargs['StatementDate']
        quarter, year = return_adjusted_quarter_and_year(self.statement_date, quarter_offset)
        self.quarter: int = quarter
        self.year: int = year

        # current assets
        self.current_assets: float = kwargs['CurrentAssets']
        self.cash_and_equivalents: float = kwargs['CashAndCashEquivalents']
        self.short_term_investments: float = \
            kwargs['CashCashEquivalentsAndShortTermInvestments'] - self.cash_and_equivalents
        self.accounts_receivable: float = kwargs['Receivables']
        self.inventory: float = kwargs['Inventory']
        self.other_current_assets: float = \
            self.current_assets - self.cash_and_equivalents - self.short_term_investments - self.accounts_receivable - \
            self.inventory

        # non current assets
        self.non_current_assets: float = kwargs['TotalNonCurrentAssets']
        self.net_ppe: float = kwargs['NetPPE']
        self.gross_ppe: float = kwargs['GrossPPE']
        self.goodwill: float = kwargs['Goodwill']
        self.other_intangibles: float = kwargs['OtherIntangibleAssets']
        self.other_non_current_assets: float = \
            self.non_current_assets - self.net_ppe - self.goodwill - self.other_intangibles

        # total assets
        self.total_assets = self.current_assets + self.non_current_assets

        # current liabilities
        self.current_liabilities: float = kwargs['CurrentLiabilities']
        self.accounts_payable: float = kwargs['Payables']
        self.accrued_liabilities: float = kwargs['CurrentAccruedExpenses']
        self.other_current_liabilities: float = \
            self.current_liabilities - self.accounts_payable - self.accrued_liabilities

        # non current liabilities
        self.non_current_liabilities: float = kwargs['TotalNonCurrentLiabilitiesNetMinorityInterest']
        self.long_term_debt: float = kwargs['LongTermDebtAndCapitalLeaseObligation']
        self.other_long_term_liabilities: float = self.non_current_liabilities - self.long_term_debt
        self.total_debt: float = kwargs['TotalDebt']

        # total liabilities
        self.total_liabilities: float = self.current_liabilities + self.non_current_liabilities

        # equity
        self.stockholders_equity: float = kwargs['StockholdersEquity']
        if 'MinorityInterest' in kwargs:
            self.minority_interest: float = kwargs['MinorityInterest']
        else:
            self.minority_interest: float = 0.0
        self.total_equity: float = self.stockholders_equity + self.minority_interest
        self.retained_earnings: float = kwargs['RetainedEarnings']
        self.n_common_shares_os: float = kwargs['OrdinarySharesNumber']

        # liabilities + equity
        self.total_liabilities_and_equity: float = self.total_liabilities + self.total_equity

        if self.total_assets - self.total_liabilities_and_equity != 0:
            self.print_balance_sheet()
            raise ValueError(f'{self.ticker} Q{self.quarter}-{self.year}: A = L + E did not compute')

    def __repr__(self):
        return f'{self.ticker}: {self.quarter}-{self.year}'

    def print_balance_sheet(self):
        print_string = ''

        items_to_print = [
            'cash_and_equivalents', 'short_term_investments', 'accounts_receivable', 'inventory',
            'other_current_assets', 'current_assets', 'net_ppe', 'goodwill', 'other_intangibles',
            'other_non_current_assets', 'non_current_assets', 'total_assets', 'accounts_payable',
            'accrued_liabilities', 'other_current_liabilities', 'current_liabilities', 'long_term_debt',
            'other_long_term_liabilities', 'non_current_liabilities', 'total_liabilities', 'stockholders_equity',
            'minority_interest', 'total_liabilities_and_equity'
        ]

        for item in items_to_print:
            print_string += f'{item}'.ljust(30)
            print_string += f'{"{:,}".format(getattr(self, item))}\n'.rjust(20)

        print(print_string)

    def return_data_list(self) -> list:

        return_list = [
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '1 - Current Assets',
             'account': '1.1 - Cash & Cash Equivalents',
             'amount': self.cash_and_equivalents
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '1 - Current Assets',
             'account': '1.2 - Short Term Investments',
             'amount': self.short_term_investments
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '1 - Current Assets',
             'account': '1.3 - Accounts Receivable',
             'amount': self.accounts_receivable
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '1 - Current Assets',
             'account': '1.4 - Inventory',
             'amount': self.inventory
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '1 - Current Assets',
             'account': '1.5 - Other Current Assets',
             'amount': self.other_current_assets
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '2 - Non-Current Assets',
             'account': '2.1 - Net PPE',
             'amount': self.net_ppe
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '2 - Non-Current Assets',
             'account': '2.2 - Goodwill',
             'amount': self.goodwill
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '2 - Non-Current Assets',
             'account': '2.3 - Other Intangible Assets',
             'amount': self.other_intangibles
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '2 - Non-Current Assets',
             'account': '2.4 - Other Non-Current Assets',
             'amount': self.other_non_current_assets
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '3 - Current Liabilities',
             'account': '3.1 - Accounts Payable',
             'amount': self.accounts_payable
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '3 - Current Liabilities',
             'account': '3.2 - Accrued Liabilities',
             'amount': self.accrued_liabilities
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '3 - Current Liabilities',
             'account': '3.3 - Other Current Liabilities',
             'amount': self.other_current_liabilities
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '4 - Non-Current Liabilities',
             'account': '4.1 - Long-Term Debt',
             'amount': self.long_term_debt
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '4 - Non-Current Liabilities',
             'account': '4.2 - Other Non-Current Liabilities',
             'amount': self.other_long_term_liabilities
             },
            {'company': self.ticker,
             'statementDate': self.statement_date,
             'quarter': self.quarter,
             'year': self.year,
             'accountClassification': '5 - Equity',
             'account': '5.1 - Stockholders Equity',
             'amount': self.total_equity
             },
        ]

        return return_list
