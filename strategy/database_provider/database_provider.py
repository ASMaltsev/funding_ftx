import psycopg2 as ps


class DataBaseProvider:

    def __init__(self):
        self.connection = ps.connect(dbname='funding_db',
                                     user="",
                                     password="",
                                     host="",
                                     port='5432')

        self.cursor = self.connection.cursor()

    def get_params(self, client_name: str) -> dict:
        self.cursor.execute(
            f"""SELECT params FROM ftx WHERE name = '{client_name}';""")
        return self.cursor.fetchone()[0]

    def close(self):
        self.cursor.close()
        self.connection.close()
