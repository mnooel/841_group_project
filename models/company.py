# models.company.py

import pandas as pd
import itertools

from models.income_statement import return_quarterly_is_df
from models.income_statement import convert_is_df_to_records_dict
from models.income_statement import combine_income_statements_to_dict
from models.income_statement import IncomeStatement
from models.balance_sheet import return_quarterly_bs_df
from models.balance_sheet import convert_bs_df_to_records_dict
from models.balance_sheet import BalanceSheet
from models.consolidated_statement import ConsolidatedStatement


class Company:

    def __init__(self, ticker: str, quarter_offset: int):
        # company info
        self.ticker: str = ticker
        self.quarter_offset: int = quarter_offset

        # income statement
        self.is_df: pd.DataFrame = return_quarterly_is_df(self.ticker)
        self.is_records_dict: dict = convert_is_df_to_records_dict(self.is_df)

        # balance sheet
        self.bs_df: pd.DataFrame = return_quarterly_bs_df(self.ticker)
        self.bs_records_dict: dict = convert_bs_df_to_records_dict(self.bs_df)

        # statement groups
        self.statement_groups = self.return_statement_groups()

    def __repr__(self):
        return f'{self.ticker}'

    def return_is_data_list(self) -> list:

        return_list = []

        for inc_stmt in self.is_records_dict:
            income_statement = IncomeStatement(ticker=self.ticker,
                                               quarter_offset=self.quarter_offset,
                                               **inc_stmt
                                               )
            return_list.append(income_statement.return_data_list())

        flat_list = list(itertools.chain(*return_list))

        return flat_list

    def return_bs_data_list(self) -> list:

        return_list = []

        for bal_sheet in self.bs_records_dict:
            balance_sheet = BalanceSheet(ticker=self.ticker,
                                         quarter_offset=self.quarter_offset,
                                         **bal_sheet
                                         )
            if balance_sheet.quarter == 4:
                return_list.append(balance_sheet.return_data_list())

        flat_list = list(itertools.chain(*return_list))

        return flat_list

    def return_statement_groups(self):

        # list of all income statement objects
        income_statement_list = [
            IncomeStatement(ticker=self.ticker, quarter_offset=self.quarter_offset, **inc_stmt)
            for inc_stmt in self.is_records_dict
        ]
        # dict of income statement objects organized by key=year
        income_statement_dict = {}
        print('')

        for inc_stmt in income_statement_list:
            if inc_stmt.year not in income_statement_dict:
                income_statement_dict[inc_stmt.year] = [inc_stmt]
            elif inc_stmt.year in income_statement_dict:
                income_statement_dict[inc_stmt.year].append(inc_stmt)

        # list of all balance sheet objects
        balance_sheet_list = [
            BalanceSheet(ticker=self.ticker, quarter_offset=self.quarter_offset, **bal_sheet)
            for bal_sheet in self.bs_records_dict
        ]

        # dict of balance sheet objects organized by key=year. only add q4 balance sheets
        balance_sheet_dict = {}

        for bal_sheet in balance_sheet_list:
            if bal_sheet.quarter == 4 and bal_sheet.year not in balance_sheet_dict:
                balance_sheet_dict[bal_sheet.year] = bal_sheet
            else:
                pass

        consolidated_statements = {}

        inc_years = list(income_statement_dict.keys())
        bs_years = list(balance_sheet_dict.keys())[:-1]
        print(f'{self.ticker} - is_years: {inc_years}')
        print(f'{self.ticker} - bs_years: {bs_years}')

        years = [year for year in inc_years if year in bs_years and year > 2000]
        print(f'{self.ticker} - du_years: {years}')

        for year in years:
            if year > 2001:
                con_stmt = ConsolidatedStatement(
                    ticker=self.ticker,
                    year=year,
                    income_statement=IncomeStatement(ticker=self.ticker,
                                                     quarter_offset=self.quarter_offset,
                                                     **combine_income_statements_to_dict(*income_statement_dict[year])),
                    balance_sheet=balance_sheet_dict[year],
                    prior_balance_sheet=balance_sheet_dict[year - 1]
                )
                consolidated_statements[year] = con_stmt

        return consolidated_statements
