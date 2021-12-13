import psycopg2 as ps
from strategy.others import USER_NAME, USER_PASS, HOST_DB


class DataBaseProvider:

    def __init__(self):
        self.connection = ps.connect(dbname='funding_db', user=USER_NAME,
                                     password=USER_PASS,
                                     host=HOST_DB,
                                     port='5432')

        self.cursor = self.connection.cursor()

    def get_strategy_hyperparams(self, client_name: str, section: str) -> dict:
        self.cursor.execute(
            f"""SELECT strategy_hyperparams FROM client_params WHERE name = '{client_name}' AND section = '{section}';
            """)
        return self.cursor.fetchone()[0]

    def get_account_hyperparams(self, client_name: str, section: str) -> dict:
        self.cursor.execute(
            f"""SELECT account_hyperparams FROM client_params WHERE name = '{client_name}' AND section = '{section}';
            """)
        return self.cursor.fetchone()[0]

    def close(self):
        self.cursor.close()
        self.connection.close()
