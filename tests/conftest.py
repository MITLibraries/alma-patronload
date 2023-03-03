import datetime
import os

import pytest
from bs4 import BeautifulSoup
from click.testing import CliRunner


@pytest.fixture(name="config_values")
def config_values_fixture():
    config_values = {
        "DATA_WAREHOUSE_USER": "user123",
        "DATA_WAREHOUSE_PASSWORD": "pass123",
        "DATA_WAREHOUSE_HOST": "http://localhost/",
        "DATA_WAREHOUSE_PORT": "1234",
        "DATA_WAREHOUSE_SID": "database5678",
        "LOG_LEVEL": "INFO",
        "S3_BUCKET_NAME": "patronload",
        "S3_PATH": "/test/example/",
        "WORKSPACE": "test",
    }
    return config_values


@pytest.fixture()
def staff_patron_null_values_record():
    return (
        "222222222",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )


@pytest.fixture()
def student_patron_null_values_record():
    return (
        "111111111",
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )


@pytest.fixture()
def staff_patron_all_values_record():
    return (
        "222222222",
        "STAFF_KRB_NAME@MIT.EDU",
        "STAFF_KRB_NAME",
        "22222222222222",
        "Doe, Jane",
        "AA-B1-11",
        "5555555555",
        datetime.datetime(2023, 6, 30, 0, 0),
        "27",
        "Staff - Lincoln Labs",
        "10000948",
        "LL-Homeland Protection & Air Traffic Con",
        "Part-time Flexible/LL",
        "Part-time Flexible/LL",
    )


@pytest.fixture()
def student_patron_all_values_record():
    return (
        "111111111",
        "STUDENT_KRB_NAME@MIT.EDU",
        "STUDENT_KRB_NAME",
        "11111111111111",
        "Doe",
        "Jane",
        "Janeth",
        "100 Smith St",
        "Apt 34",
        "Cambridge",
        "MA",
        "00000",
        "5555555555",
        "4444444444",
        "3333333333",
        "G",
        "1",
    )


@pytest.fixture()
def staff_patron_template():
    with open("config/staff_template.xml", "r", encoding="utf8") as xml_template:
        return BeautifulSoup(xml_template, features="xml")


@pytest.fixture()
def student_patron_template():
    with open("config/student_template.xml", "r", encoding="utf8") as xml_template:
        return BeautifulSoup(xml_template, features="xml")


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def test_env(config_values):
    os.environ = config_values
    yield
