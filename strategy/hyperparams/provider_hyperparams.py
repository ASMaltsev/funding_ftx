from strategy.database_provider.database_provider import DataBaseProvider
from strategy.others import LABEL, SECTION


class HyperParams:

    def __init__(self):
        self.database_provider = None
        self.strategy_hyperparams = None
        self.account_hyperparams = None

    def update_data(self):
        self.database_provider = DataBaseProvider()
        self.strategy_hyperparams = self.database_provider.get_strategy_hyperparams(client_name=LABEL,
                                                                                    section=SECTION)
        self.account_hyperparams = self.database_provider.get_account_hyperparams(client_name=LABEL,
                                                                                  section=SECTION)
        self.database_provider.close()

    def get_base_fr_earn(self):
        return self.strategy_hyperparams['base_fr_earn']

    def get_A(self):
        return self.strategy_hyperparams['A']

    def get_k(self):
        return self.strategy_hyperparams['k']

    def get_time_exit(self):
        return self.strategy_hyperparams['time_exit']

    def get_save_time(self):
        return self.strategy_hyperparams['save_time']

    def get_share(self, section):
        return self.account_hyperparams['section'][section]['share']

    def get_all_tickers(self, section):
        all_tickers = []
        assets_info = self.account_hyperparams['section'][section]['assets']
        for asset, tickers in assets_info.items():
            all_tickers.append(tickers['perp'])
            if section == 'USDT-M':
                all_tickers.append(tickers['quart'])
            elif section == 'COIN-M':
                all_tickers.append(tickers['current'])
                all_tickers.append(tickers['next'])
        return all_tickers

    def get_assets(self, section):
        return list(self.account_hyperparams['section'][section]['assets'].keys())

    def get_list_tickers(self, section: str, kind: str):
        """
        @param section: USDT-M or COIN-M
        @param kind: perp, next, current, quart
        @return: list of tickers
        """
        arr = []
        for asset, tickers in self.account_hyperparams['section'][section]['assets'].items():
            arr.append(tickers[kind])
        return arr

    def get_ticker_by_asset(self, section: str, asset: str, kind: str):
        return self.account_hyperparams['section'][section]['assets'][asset][kind]

    def get_min_batch_size(self, section: str, asset: str) -> float:
        return float(self.account_hyperparams['section'][section]['assets'][asset]['min_batch_size'])

    def get_sections(self) -> list:
        return list(set(self.account_hyperparams['section'].keys()).intersection({'USDT-M', 'COIN-M'}))

    def get_max_leverage(self, section):
        return self.account_hyperparams['section'][section]['leverages']['leverage_max']

    def get_max_ignore(self, section):
        return self.account_hyperparams['section'][section]['leverages']['leverage_max_ignore']

    def get_limit_amount(self, section, asset):
        return self.account_hyperparams['section'][section]['assets'][asset]['limit_amount']
