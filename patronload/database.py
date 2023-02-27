from typing import Generator

import oracledb


def build_sql_query(fields: list, table: str) -> str:
    """
    Build a SQL query for an Oracle database from a list of fields and a table name.

    Args:
        fields: The list of fields to retrieve.
        table: The table to retrieve the fields from.
    """
    query = "SELECT " + ", ".join(fields)
    query += " FROM " + table
    return query


def create_database_connection(config_values: dict) -> oracledb.Connection:
    """
    Create a connection to an Oracle database for submitting queries.

    Args:
        config_values: A dict with the necessary values to configure an
        Oracle database connection.
    """
    oracledb.init_oracle_client()
    connection_parameters = oracledb.ConnectParams(
        user=config_values["DATA_WAREHOUSE_USER"],
        password=config_values["DATA_WAREHOUSE_PASSWORD"],
        host=config_values["DATA_WAREHOUSE_HOST"],
        port=config_values["DATA_WAREHOUSE_PORT"],
        sid=config_values["DATA_WAREHOUSE_SID"],
    )
    return oracledb.connect(params=connection_parameters)


def query_database_for_patron_records(
    connection: oracledb.Connection, query: str
) -> Generator:
    """
    Query Oracle Database for patron record information.

    Args:
        connection: An Oracle database connection.
        query: A SQL query to submit via the Oracle database connection.

    """
    cursor = connection.cursor()
    cursor.execute(query)
    for patron_record in cursor.fetchall():
        yield patron_record
