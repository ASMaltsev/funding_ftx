from strategy.alpha import FundingAlpha
from strategy.executor import DadExecutor

api_key = 'IdPorsZNdskqCUNbO5aN0w6TY67Kfl0syZjHDV3ZP9tOMuM6k3KzovNizMKmBpix'
secret_key = '7qE1lC0fVpNF7i9Lb08odC1HaV6m2LILmzy2SSEnAXTwqOVaJhqA8cVz1tzPzP0A'

instructions = FundingAlpha().decide()
DadExecutor(api_key=api_key, secret_key=secret_key).execute(instructions)
