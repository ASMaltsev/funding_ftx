from strategy.hyperparams.hyperparameters import strategy_hyperparams, account_hyperparams


class ProviderHyperParamsStrategy:

    @staticmethod
    def get_base_fr_earn():
        return strategy_hyperparams['base_fr_earn']

    @staticmethod
    def get_A():
        return strategy_hyperparams['A']

    @staticmethod
    def get_k():
        return strategy_hyperparams['k']

    @staticmethod
    def get_time_exit():
        return strategy_hyperparams['time_exit']

    @staticmethod
    def get_save_time():
        return strategy_hyperparams['save_time'](strategy_hyperparams['time_exit'])

    @staticmethod
    def get_share(section):
        return strategy_hyperparams[section]['share']

    @staticmethod
    def get_all_tickers(section):
        all_tickers = []
        assets_info = strategy_hyperparams[section]['assets']
        for asset, tickers in assets_info.items():

            all_tickers.append(tickers['perp'])

            if section == 'USDT-M':
                all_tickers.append(tickers['quart'])
            elif section == 'COIN-M':
                all_tickers.append(tickers['current'])
                all_tickers.append(tickers['next'])

        return all_tickers

    @staticmethod
    def get_assets(section):
        return list(strategy_hyperparams[section]['assets'].keys())

    @staticmethod
    def get_list_tickers(section: str, kind: str):
        """
        @param section: USDT-M or COIN-M
        @param kind: perp, next, current, quart
        @return: list of tickers
        """
        arr = []
        for asset, tickers in strategy_hyperparams[section]['assets'].items():
            arr.append(tickers[kind])
        return arr

    @staticmethod
    def get_ticker_by_asset(section: str, asset: str, kind: str):
        return strategy_hyperparams[section]['assets'][asset][kind]


class AccountHyperParams:

    @staticmethod
    def get_max_leverage(section):
        return account_hyperparams[section]['leverage_max']
