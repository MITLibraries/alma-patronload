from unittest.mock import MagicMock, patch

from patronload.database import (
    build_sql_query,
    create_database_connection,
    query_database,
)


def test_build_sql_query():
    assert build_sql_query(["NAME", "DATE"], "TABLE") == "SELECT NAME, DATE FROM TABLE"


@patch("patronload.database.oracledb")
def test_create_database_connection_success(mocked_oracledb, config_values):
    create_database_connection(config_values)
    mocked_oracledb.init_oracle_client.assert_called()
    mocked_oracledb.ConnectParams.assert_called()
    mocked_oracledb.connect.assert_called()


def test_query_database_success():
    query = "SELECT ROW1 FROM TABLE1"
    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = [("1", "2"), ("3", "4")]
    assert query_database(connection, query) == [("1", "2"), ("3", "4")]
