from db import connection
from defaults import DATABASE_NAME


def delete():
    connection.drop_database(DATABASE_NAME)


if __name__ == '__main__':
    delete()
