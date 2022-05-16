#!/usr/bin/env python

from strategy.executor.ftx_executor.executor import FtxExecutor
from strategy.database_provider.database_provider import DataBaseProvider

if __name__ == '__main__':
    api_key = ''
    secret_key = ''

    db_provider = DataBaseProvider()
    params = db_provider.get_params('test')

    FtxExecutor(api_key=api_key, secret_key=secret_key, **params).execute()
