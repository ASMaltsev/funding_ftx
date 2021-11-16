#!/usr/bin/env python

from strategy.executor import DadExecutor
from strategy.others import API_KEY, SECRET_KEY

DadExecutor(api_key=API_KEY, secret_key=SECRET_KEY).execute()
