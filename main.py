#!/usr/bin/env python

from strategy.executor import DadExecutor
from strategy.others import LABEL
from strategy.others.constants import Keys

keys = Keys()

DadExecutor(api_key=keys.API_KEY, secret_key=keys.SECRET_KEY).execute()
