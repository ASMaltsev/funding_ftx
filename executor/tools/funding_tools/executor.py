from executor.tools.abstract_tools.abstract_executor import AbstractExecutor
from executor.tools.funding_tools.parser_actions import ParserActions


class FundingExecutor(AbstractExecutor):

    def __init__(self, api_key: str, secret_key: str):
        super().__init__(api_key, secret_key)

    def execute(self, actions: dict) -> bool:
        parser = ParserActions(actions)
        action_for_execute = parser.parse()

        return True
