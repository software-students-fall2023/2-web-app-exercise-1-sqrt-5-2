from defaults import DATABASE_NAME
from db import connection

def delete():
    connection.drop_database(DATABASE_NAME)


if __name__ == '__main__':
    delete()
