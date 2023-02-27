from unittest.mock import MagicMock, patch

import pytest
from oracledb import DatabaseError

from patronload.database import (
    build_sql_query,
    create_database_connection,
    query_database_for_patron_records,
)


def test_build_sql_query():
    assert build_sql_query(["NAME", "DATE"], "TABLE") == "SELECT NAME, DATE FROM TABLE"


@patch("patronload.database.oracledb")
def test_create_database_connection_success(mocked_oracledb, config_values):
    create_database_connection(config_values)
    mocked_oracledb.init_oracle_client.assert_called()
    mocked_oracledb.ConnectParams.assert_called()
    mocked_oracledb.connect.assert_called()


@patch("patronload.database.oracledb")
def test_create_database_connection_raises_exception(mocked_oracledb, config_values):
    mocked_oracledb.init_oracle_client.side_effect = DatabaseError
    with pytest.raises(DatabaseError):
        create_database_connection(config_values)


def test_query_database_for_patron_records_success():
    query = "SELECT ROW1 FROM TABLE1"
    connection = MagicMock()
    connection.cursor.return_value.fetchall.return_value = iter(["1", "2", "3"])
    results = query_database_for_patron_records(connection, query)
    assert next(results) == "1"
    assert next(results) == "2"
    assert next(results) == "3"
