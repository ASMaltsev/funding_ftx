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
    def get_tickers(section):
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


class AccountHyperParams:

    @staticmethod
    def get_max_leverage(section):
        return account_hyperparams[section]['leverage_max']
