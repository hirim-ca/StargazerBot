import psycopg2
import pandas as pd

class PostgreSQL:
    """ A postgresql controller that connects and communicates with postgresql DBs. """

    def __init__(self, **kwargs):

        self.user = kwargs.get("user")
        self.password = kwargs.get("password")
        self.host = kwargs.get("host")
        self.port = kwargs.get("port")
        self.database = kwargs.get("database")

        self.conn = None
        self.cursor = None

    def connect(self):  
        """ Establish a connection with the database. """

        try:
            self.conn = psycopg2.connect(
                user = self.user,
                password = self.password,
                host = self.host,
                port = self.port,
                database = self.database
            )

            self.cursor = self.conn.cursor()

            print(f"\nPostgreSQL: Connected to { self.host }.")

            self.cursor.execute("SELECT version();")
            version = self.cursor.fetchone()
            print(f"\tversion - { version }")

        except (Exception, psycopg2.Error) as ex:
            print(f"\tError while connecting to { self.host }", end="\n\t")
            print(ex)

    def closeConn(self):
        """ Closes the psycopg connection """
        if self.conn:
            self.cursor.close()
            self.conn.close()
            self.conn = None
            self.cursor = None

            print(f"\tConnection to { self.host } is closed.\n")

    # public functions

    def execute_query(self, query, commit=False):
        """ 
        Executes the specified query to the database, returns None. 
        Usually not called.
        """

        try:
            self.connect()
            if not self.conn: return
        
            self.cursor.execute(query)
            if commit: self.conn.commit()

            print(f"\tQuery: '{ query }' executed successfully.")

        except (Exception, psycopg2.DatabaseError) as ex:
            print(f"\tFailed to execute: '{ query }'")
            print(ex)

        finally:
            self.closeConn()

    def insert(self, table, **kwargs):
        """ 
        Insert values into the table specified. 
        Usage: insert(table, {column=value})
        """

        try:
            self.connect()
            if not self.conn: return
        
            # format query

            keys = ",".join(kwargs.keys())
            contents = ",".join(kwargs.values())

            query = f"INSERT INTO { table } ({ keys }) VALUES ({ contents })"

            # execute query

            self.cursor.execute(query)
            self.conn.commit()

            print(f"\tValues inserted to { table } successfully.")

        except (Exception, psycopg2.DatabaseError) as ex:
            print(f"\tFailed to insert into { table }.", end="\n\t")
            print(ex)

        finally:
            self.closeConn()

    def update(self, table, constraints, **kwargs):
        """ 
        Update values from the table specified. 
        Usage: update(table, constraints='constaints', {column=value})
        """

        try:
            self.connect()
            if not self.conn: return
        
            # format query

            set_ = ""

            for (key, value) in kwargs.items():
                set_ += f"{ key } = { value }, "

            set_ = set_[:-2]

            query = f"UPDATE { table } SET { set_ } { constraints }"

            # execute query

            self.cursor.execute(query)
            self.conn.commit()

            print(f"\tValues in { table } updated successfully.")

        except (Exception, psycopg2.DatabaseError) as ex:
            print(f"\tFailed to updated { table }.", end="\n\t")
            print(ex)

        finally:
            self.closeConn()

    def get(self, table, columns, constraints):
        """ 
        Extract values from table with specified constraints. 
        Returns a pd.DataFrame if values exist.
        Usage: get(table, columns=[columns], constraints='constraints')
        """

        result = None

        try:
            self.connect()
            if not self.conn: return

            # format query

            columns_ = ",".join(columns)

            query = f"SELECT { columns_ } FROM { table } { constraints }"

            # execute query
            
            self.cursor.execute(query)
            result = pd.DataFrame(self.cursor.fetchall(), columns=columns)

            
            print(f"\tValues extracted from { table } successfully.")

        except (Exception, psycopg2.DatabaseError) as ex:
            print(f"\tFailed to get values from { table }.", end="\n\t")
            print(ex)
            return None

        finally:
            self.closeConn()
            return result

    def delete(self, table, constraints):
        """ 
        Delete values from table with specified constrains. 
        Usage: get(table, constraints='constraints')
        """

        try:
            self.connect()
            if not self.conn: return

            # format query

            query = f"DELETE FROM { table } { constraints }"

            # execute query
            
            self.cursor.execute(query)
            self.conn.commit()

            print(f"\tValues deleted from { table } successfully.")

        except (Exception, psycopg2.DatabaseError) as ex:
            print(f"\tFailed to delete values from { table }.", end="\n\t")
            print(ex)

        finally:
            self.closeConn()