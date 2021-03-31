# models.consolidated_statement.py

from datetime import datetime, timedelta
import pandas as pd

from .income_statement import IncomeStatement
from .balance_sheet import BalanceSheet


def return_market_close_dict(ticker: str) -> dict:
    path = f'fin_data_input/{ticker}.csv'

    df = pd.read_csv(path)

    data_dict = {}

    for index, row in df.iterrows():
        data_dict[row['Date']] = row['Close']

    return data_dict


def return_market_close(ticker: str, statement_date: datetime) -> float:

    dict = return_market_close_dict(ticker=ticker)
    price_date = statement_date + timedelta(days=1)
    str_date = price_date.strftime('%Y-%m-%d')

    return dict[str_date]


class ConsolidatedStatement:

    def __init__(self, ticker: str,
                 year: int, income_statement: IncomeStatement,
                 balance_sheet: BalanceSheet,
                 prior_balance_sheet: BalanceSheet):
        # company and base objects
        self.ticker: str = ticker
        self.year: int = year
        self.income_statement: IncomeStatement = income_statement
        self.balance_sheet: BalanceSheet = balance_sheet
        self.prior_balance_sheet: BalanceSheet = prior_balance_sheet

        # profitability ratios
        if self.income_statement.revenue == 0:
            self.gross_margin: float = 0
            self.operating_margin: float = 0
            self.ebitda_margin: float = 0
            self.net_profit_margin: float = 0
        else:
            self.gross_margin: float = self.income_statement.gross_profit / self.income_statement.revenue
            self.operating_margin: float = self.income_statement.operating_income / self.income_statement.revenue
            self.ebitda_margin: float = self.income_statement.ebitda / self.income_statement.revenue
            self.net_profit_margin: float = self.income_statement.net_income / self.income_statement.revenue

        # liquidity ratios
        self.current_ratio: float = self.balance_sheet.current_assets / self.balance_sheet.current_liabilities
        self.quick_ratio: float = (
                    self.balance_sheet.cash_and_equivalents +
                    self.balance_sheet.short_term_investments +
                    self.balance_sheet.accounts_receivable
        ) / self.balance_sheet.current_liabilities
        self.cash_ratio: float = self.balance_sheet.cash_and_equivalents / self.balance_sheet.current_liabilities

        # working capital ratios
        # days ratios
        self.current_working_capital: float = \
            self.balance_sheet.current_assets - self.balance_sheet.current_liabilities
        self.prior_working_capital: float = \
            self.prior_balance_sheet.current_assets - self.prior_balance_sheet.current_liabilities
        if self.income_statement.revenue == 0:
            self.ar_days: float = 0
        else:
            self.ar_days: float = self.balance_sheet.accounts_receivable / (self.income_statement.revenue / 365)
        if self.income_statement.cogs == 0:
            self.ap_days: float = 0
            self.invent_days: float = 0
        else:
            self.ap_days: float = self.balance_sheet.accounts_payable / (self.income_statement.cogs / 365) * -1
            self.invent_days: float = self.balance_sheet.inventory / (self.income_statement.cogs / 365) * -1
        self.cash_conversion_cycle: float = self.invent_days + self.ar_days - self.ap_days
        # turnover ratios
        avg_ar: float = (self.balance_sheet.accounts_receivable + self.prior_balance_sheet.accounts_receivable) / 2
        self.ar_turnover: float = self.income_statement.revenue / avg_ar
        avg_inv: float = (self.balance_sheet.inventory + self.prior_balance_sheet.inventory) / 2
        self.invent_turnover: float = self.income_statement.cogs / avg_inv * -1
        avg_ap: float = (self.balance_sheet.accounts_payable + self.prior_balance_sheet.accounts_payable) / 2
        self.ap_turnover: float = self.income_statement.cogs / avg_ap * -1
        avg_working_capital: float = (self.current_working_capital + self.prior_working_capital) / 2
        self.working_cap_turnover: float = self.income_statement.revenue / avg_working_capital

        # interest coverage ratios
        if self.income_statement.interest_exp == 0:
            self.ebit_interest_coverage: float = 0
            self.ebitda_interest_coverage: float = 0
        else:
            self.ebit_interest_coverage: float = \
                self.income_statement.ebit / self.income_statement.interest_exp
            self.ebitda_interest_coverage: float = \
                self.income_statement.ebitda / self.income_statement.interest_exp

        # market close price
        self.market_close: float = return_market_close(ticker=self.ticker,
                                                       statement_date=self.balance_sheet.statement_date)

        # leverage ratios
        self.debt_to_capital: float = \
            self.balance_sheet.total_debt / (self.balance_sheet.total_debt + self.balance_sheet.total_equity)
        self.debt_to_equity: float = \
            self.balance_sheet.total_debt / self.balance_sheet.total_equity
        # enterprise value
        self.net_debt: float = self.balance_sheet.total_liabilities - self.balance_sheet.cash_and_equivalents
        self.market_capitalization: float = self.market_close * self.balance_sheet.n_common_shares_os
        self.enterprise_value: float = \
            self.market_capitalization + self.balance_sheet.total_liabilities - self.balance_sheet.cash_and_equivalents
        self.debt_to_enterprise_value: float = self.balance_sheet.total_liabilities / self.enterprise_value
        self.equity_multiplier_book: float = self.balance_sheet.total_assets / self.balance_sheet.total_equity
        self.equity_multiplier_marker: float = self.enterprise_value / self.market_capitalization

        # industry specific ratios
        self.r_and_d_to_sales: float = \
            self.income_statement.research_and_development / self.income_statement.revenue * -1
        self.capx: float = \
            self.balance_sheet.gross_ppe - self.prior_balance_sheet.gross_ppe + self.income_statement.dep_and_amort
        self.capx_to_sales: float = self.capx / self.income_statement.revenue

        # valuation ratios
        self.market_to_book: float = self.market_capitalization / self.balance_sheet.total_equity
        self.market_to_sales: float = self.market_capitalization / self.income_statement.revenue
        self.ev_to_ebitda: float = self.enterprise_value / self.income_statement.ebitda
        self.ev_to_sales: float = self.enterprise_value / self.income_statement.revenue
        self.eps_diluted: float = self.income_statement.eps_diluted
        self.eps_basic: float = \
            (self.income_statement.net_income - self.income_statement.ps_div) / self.balance_sheet.n_common_shares_os
        self.price_to_earnings: float = self.market_close / self.eps_basic

        # operating ratios
        avg_total_assets: float = (self.balance_sheet.total_assets + self.prior_balance_sheet.total_assets) / 2
        self.asset_turnover: float = self.income_statement.revenue / avg_total_assets
        self.return_on_assets: float = self.income_statement.net_income / self.balance_sheet.total_assets
        self.return_on_equity: float = self.income_statement.net_income / self.balance_sheet.total_equity
        self.return_on_invested_capital: float = self.income_statement.nopat / self.balance_sheet.total_assets

        # altman Z Score values
        self.working_capital_to_total_assets: float = self.current_working_capital / self.balance_sheet.total_assets
        self.re_to_total_assets: float = self.balance_sheet.retained_earnings / self.balance_sheet.total_assets
        self.ebit_to_total_assets: float = self.income_statement.ebit / self.balance_sheet.total_assets
        self.market_value_of_equity_to_liabs: float = self.market_capitalization / self.balance_sheet.total_liabilities
        self.total_sales_to_total_assets: float = self.income_statement.revenue / self.balance_sheet.total_assets
        self.alt_z_score: float = \
            (1.2 * self.working_capital_to_total_assets) + \
            (1.4 * self.re_to_total_assets) + \
            (3.3 * self.ebit_to_total_assets) + \
            (0.6 * self.market_value_of_equity_to_liabs) + \
            (1.0 * self.total_sales_to_total_assets)

    def __repr__(self):
        return f'{self.ticker}: {self.year}'

    def return_data_list(self) -> list:

        return_list = [
            # Profitability Ratios
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '1 - Profitability Ratios',
             'ratio': '1.1 - Gross Margin',
             'value': self.gross_margin
            },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '1 - Profitability Ratios',
             'ratio': '1.2 - Operating Margin',
             'value': self.operating_margin
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '1 - Profitability Ratios',
             'ratio': '1.3 - EBITDA Margin',
             'value': self.ebitda_margin
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '1 - Profitability Ratios',
             'ratio': '1.4 - Net Profit Margin',
             'value': self.net_profit_margin
             },
            # Liquidity Ratios
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '2 - Liquidity Ratios',
             'ratio': '2.1 - Current Ratio',
             'value': self.current_ratio
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '2 - Liquidity Ratios',
             'ratio': '2.2 - Quick Ratio',
             'value': self.quick_ratio
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '2 - Liquidity Ratios',
             'ratio': '2.3- Cash Ratio',
             'value': self.cash_ratio
             },
            # Working Cap Ratios
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '3 - Working Capital Ratios',
             'ratio': '3.1 - Days in A/R',
             'value': self.ar_days
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '3 - Working Capital Ratios',
             'ratio': '3.2 - A/R Turnover',
             'value': self.ar_turnover
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '3 - Working Capital Ratios',
             'ratio': '3.3 - Days in Inventory',
             'value': self.invent_days
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '3 - Working Capital Ratios',
             'ratio': '3.4 - Inventory Turnover',
             'value': self.invent_turnover
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '3 - Working Capital Ratios',
             'ratio': '3.5 - Days in A/P',
             'value': self.ap_days
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '3 - Working Capital Ratios',
             'ratio': '3.6 - A/P Turnover',
             'value': self.ap_turnover
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '3 - Working Capital Ratios',
             'ratio': '3.7 - Cash Conversion Cycle',
             'value': self.cash_conversion_cycle
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '3 - Working Capital Ratios',
             'ratio': '3.8 - Working Capital Turnover',
             'value': self.working_cap_turnover
             },
            # Interest Coverage Ratios
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '4 - Interest Coverage Ratios',
             'ratio': '4.1 - EBIT / Interest Coverage Ratio',
             'value': self.ebit_interest_coverage
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '4 - Interest Coverage Ratios',
             'ratio': '4.2 - EBITDA / Interest Coverage Ratio',
             'value': self.ebitda_interest_coverage
             },
            # Leverage Ratio
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '5 - Leverage Ratios',
             'ratio': '5.1 - Debt-to-Capital Ratio',
             'value': self.debt_to_capital
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '5 - Leverage Ratios',
             'ratio': '5.2 - Debt-to-Equity Ratio',
             'value': self.debt_to_equity
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '5 - Leverage Ratios',
             'ratio': '5.3 - Debt-to-Enterprise Value Ratio',
             'value': self.debt_to_enterprise_value
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '5 - Leverage Ratios',
             'ratio': '5.4 - Equity Multiplier (book)',
             'value': self.equity_multiplier_book
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '5 - Leverage Ratios',
             'ratio': '5.5 - Equity Multiplier (market)',
             'value': self.equity_multiplier_marker
             },
            # Industry Specific Ratios
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '6 - Industry Specific Ratios',
             'ratio': '6.1 - R&D-to-Sales',
             'value': self.r_and_d_to_sales
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '6 - Industry Specific Ratios',
             'ratio': '6.2 - CAPEX-to-Sales',
             'value': self.capx_to_sales
             },
            # Valuation Ratios
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '7 - Valuation Ratios',
             'ratio': '7.1 - Market-to-Book Ratio',
             'value': self.market_to_book
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '7 - Valuation Ratios',
             'ratio': '7.2 - Price-to-Earning Ratio',
             'value': self.price_to_earnings
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '7 - Valuation Ratios',
             'ratio': '7.3 - Market-to-Sales Ratio',
             'value': self.market_to_sales
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '7 - Valuation Ratios',
             'ratio': '7.4 - EV-to-EBITDA Ratio',
             'value': self.ev_to_ebitda
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '7 - Valuation Ratios',
             'ratio': '7.5 - EV-to-Sales Ratio',
             'value': self.ev_to_sales
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '7 - Valuation Ratios',
             'ratio': '7.6 - EPS (Fully Diluted)',
             'value': self.eps_diluted
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '7 - Valuation Ratios',
             'ratio': '7.7.1 - Share Price',
             'value': self.market_close
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '7 - Valuation Ratios',
             'ratio': '7.7.2 - Common Shares O/S',
             'value': self.balance_sheet.n_common_shares_os
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '7 - Valuation Ratios',
             'ratio': '7.7.3 - Market Capitalization (Share Price * Common Shares O/S)',
             'value': self.market_capitalization
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '7 - Valuation Ratios',
             'ratio': '7.7.4 - Net Debt',
             'value': self.net_debt
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '7 - Valuation Ratios',
             'ratio': '7.7.5 - Enterprise Value',
             'value': self.enterprise_value
             },
            # Operating Ratios
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '8 - Operating Ratios',
             'ratio': '8.1 - Asset Turnover',
             'value': self.asset_turnover
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '8 - Operating Ratios',
             'ratio': '8.2 - Return on Assets (ROA)',
             'value': self.return_on_assets
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '8 - Operating Ratios',
             'ratio': '8.3 - Return on Equity (ROE)',
             'value': self.return_on_equity
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '8 - Operating Ratios',
             'ratio': '8.4 - Return on Invested Capital (ROIC)',
             'value': self.return_on_invested_capital
             },
            # Alman Z-Score
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '9 - Altman Z-Score',
             'ratio': '9.1 - Altman Z-Score (1.2A + 1.4B + 3.3C + 0.6D + 1.0E)',
             'value': self.alt_z_score
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '9 - Altman Z-Score',
             'ratio': '9.1.A - Working Capital / Total Assets Ratio',
             'value': self.working_capital_to_total_assets
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '9 - Altman Z-Score',
             'ratio': '9.1.B - Retained Earnings / Total Assets Ratio',
             'value': self.re_to_total_assets
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '9 - Altman Z-Score',
             'ratio': '9.1.C - EBIT / Total Assets Ratio',
             'value': self.ebit_to_total_assets
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '9 - Altman Z-Score',
             'ratio': '9.1.D - Market Value of Equity / Total Liabilities',
             'value': self.market_value_of_equity_to_liabs
             },
            {'company': self.ticker,
             'year': self.year,
             'ratio_type': '9 - Altman Z-Score',
             'ratio': '9.1.E - Total Sales / Total Assets',
             'value': self.total_sales_to_total_assets
             },
        ]

        return return_list
