#!/usr/bin/env python

from strategy.executor import DadExecutor
from strategy.others import LABEL
from strategy.others.constants import get_secret

get_secret(LABEL)

DadExecutor().execute()
