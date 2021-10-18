from executor.tools.abstract_tools.abstract_executor import AbstractExecutor
from executor.tools.funding_tools.parser_actions import ParserActions
from executor.tools.funding_tools.binance_data_provider import ExecutorDataProvider


class FundingExecutor(AbstractExecutor):

    def __init__(self, api_key: str, secret_key: str):
        super().__init__(api_key, secret_key)
        self.data_provider = ExecutorDataProvider(api_key, secret_key)

    def execute(self, actions: dict) -> bool:
        parser = ParserActions(actions)

        actions_for_execute = parser.parse()
        self._execute(actions_for_execute)
        return True

    def _execute(self, actions_for_execute) -> bool:
        return True
