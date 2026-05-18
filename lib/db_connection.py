import os

import psycopg2


class DBConnection:
    _instancia = None  # tu sa uklada jedina instancia

    def __new__(cls):
        if cls._instancia is None:
            # prva volanie - vytvori sa spojenie
            cls._instancia = super().__new__(cls)
            cls._instancia.conn = psycopg2.connect(
                host=os.environ.get("DB_HOST", "localhost"),
                port=int(os.environ.get("DB_PORT", 5432)),
                dbname=os.environ.get("DB_NAME", "db.test"),
                user=os.environ.get("DB_USER", "michi"),
                password=os.environ.get("DB_PASSWORD", "asd123"),
            )
            cls._instancia.cur = cls._instancia.conn.cursor()
        # kazde dalsie volanie vrati uz existujucu instanciu
        return cls._instancia
    
    def execute(self, sql, params=None):
        self.cur.execute(sql, params)

    def fetch_all(self, sql, params=None):
        self.cur.execute(sql, params)
        return self.cur.fetchall()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()
        DBConnection._instancia = None  # reset - umozni nove spojenie po close()
