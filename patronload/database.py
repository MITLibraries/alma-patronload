import json
import os
from typing import Sequence

import oracledb


def build_sql_query(fields: Sequence[str], table: Sequence[str]) -> str:
    """
    Build a SQL query for an Oracle database from a list of fields and a table name.

    Args:
        fields: The list of fields to retrieve.
        table: The table to retrieve the fields from.
    """
    query = "SELECT " + ", ".join(fields)
    query += " FROM " + str(table)
    return query


def create_database_connection(config_values: dict[str, str]) -> oracledb.Connection:
    """
    Create a connection to an Oracle database for submitting queries.

    Args:
        config_values: A dict with the necessary values to configure an
        Oracle database connection.
    """
    cloud_connector = json.loads(config_values["DATAWAREHOUSE_CLOUDCONNECTOR_JSON"])
    oracledb.init_oracle_client(lib_dir=os.getenv("ORACLE_LIB_DIR"))
    connection_parameters = oracledb.ConnectParams(
        user=cloud_connector["USER"],
        password=cloud_connector["PASSWORD"],
        host=cloud_connector["HOST"],
        port=cloud_connector["PORT"],
        sid=cloud_connector["PATH"],
    )
    return oracledb.connect(params=connection_parameters)


def query_database(connection: oracledb.Connection, query: str) -> list[tuple]:
    """
    Submit a SQL query to an Oracle Database and retrieve the results.

    Args:
        connection: An Oracle database connection.
        query: A SQL query to submit via the Oracle database connection.

    """
    cursor = connection.cursor()
    cursor.execute(query)
    return cursor.fetchall()
