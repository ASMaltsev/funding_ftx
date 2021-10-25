from strategy.executor import FundingExecutor
# from strategy.alpha import FundingAlpha
import time


def _get_decide(funding_strategy):
    try:
        decide = funding_strategy.decide()
        return decide
    except Exception as e:
        raise NotImplementedError


def _make_execute(funding_executor: FundingExecutor, action: dict):
    try:
        flag = funding_executor.execute(action)
        return flag
    except Exception as e:
        raise NotImplementedError


if __name__ == '__main__':
    api_key_client = ''
    secret_key_client = ''

    executor = FundingExecutor(api_key=api_key_client, secret_key=secret_key_client, section='USDT-M')
    # strategy = FundingAlpha()
    while True:
        decide = None
        try:
            pass
            # decide = _get_decide(strategy)
        except Exception as e:
            pass

        try:
            flag = _make_execute(executor, decide)
        except Exception as e:
            pass

        finally:
            # make risk control
            pass
        time.sleep(60 * 60 * 3)
