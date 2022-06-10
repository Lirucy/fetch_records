from peewee import PostgresqlDatabase

DATABASE = PostgresqlDatabase('fetch_records_db')

def initialize(tables):
    DATABASE.connect()
    DATABASE.create_tables(tables, safe=True)
    print("Some tables were created!")
    DATABASE.close()