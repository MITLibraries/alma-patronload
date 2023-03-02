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
def staff_patron_all_values_dict():
    return {
        "FULL_NAME": "Doe, Jane",
        "OFFICE_ADDRESS": "AA-B1-11",
        "OFFICE_PHONE": "5555555555",
        "MIT_ID": "222222222",
        "EMAIL_ADDRESS": "STAFF_KRB_NAME@MIT.EDU",
        "APPOINTMENT_END_DATE": datetime.datetime(2023, 6, 30, 0, 0),
        "KRB_NAME_UPPERCASE": "STAFF_KRB_NAME",
        "LIBRARY_PERSON_TYPE_CODE": "27",
        "LIBRARY_PERSON_TYPE": "Staff - Lincoln Labs",
        "ORG_UNIT_ID": "10000948",
        "ORG_UNIT_TITLE": "LL-Homeland Protection & Air Traffic Con",
        "POSITION_TITLE": "Part-time Flexible/LL",
        "DIRECTORY_TITLE": "Part-time Flexible/LL",
        "LIBRARY_ID": "33333333333333",
    }


@pytest.fixture()
def staff_patron_null_values_dict():
    return {
        "FULL_NAME": None,
        "OFFICE_ADDRESS": None,
        "OFFICE_PHONE": None,
        "MIT_ID": None,
        "EMAIL_ADDRESS": "STAFF_KRB_NAME@MIT.EDU",
        "APPOINTMENT_END_DATE": None,
        "KRB_NAME_UPPERCASE": None,
        "LIBRARY_PERSON_TYPE_CODE": None,
        "LIBRARY_PERSON_TYPE": None,
        "ORG_UNIT_ID": None,
        "ORG_UNIT_TITLE": None,
        "POSITION_TITLE": None,
        "DIRECTORY_TITLE": None,
        "LIBRARY_ID": None,
    }


@pytest.fixture()
def student_patron_all_values_dict():
    return {
        "MIT_ID": "111111111",
        "LAST_NAME": "Doe",
        "FIRST_NAME": "Jane",
        "MIDDLE_NAME": "Janeth",
        "TERM_STREET1": "100 Smith St",
        "TERM_STREET2": "Apt 34",
        "TERM_CITY": "Cambridge",
        "TERM_STATE": "MA",
        "TERM_ZIP": "00000",
        "TERM_PHONE1": "5555555555",
        "TERM_PHONE2": "4444444444",
        "OFFICE_PHONE": "3333333333",
        "STUDENT_YEAR": "G",
        "EMAIL_ADDRESS": "STUDENT_KRB_NAME@MIT.EDU",
        "KRB_NAME_UPPERCASE": "STUDENT_KRB_NAME",
        "HOME_DEPARTMENT": "1",
        "LIBRARY_ID": "11111111111111",
    }


@pytest.fixture()
def student_patron_null_values_dict():
    return {
        "EMAIL_ADDRESS": "STUDENT_KRB_NAME@MIT.EDU",
        "FIRST_NAME": None,
        "HOME_DEPARTMENT": None,
        "KRB_NAME_UPPERCASE": None,
        "LAST_NAME": None,
        "LIBRARY_ID": None,
        "MIDDLE_NAME": None,
        "MIT_ID": None,
        "OFFICE_PHONE": None,
        "STUDENT_YEAR": None,
        "TERM_CITY": None,
        "TERM_PHONE1": None,
        "TERM_PHONE2": None,
        "TERM_STATE": None,
        "TERM_STREET1": None,
        "TERM_STREET2": None,
        "TERM_ZIP": None,
    }


@pytest.fixture()
def staff_patron_null_values_record():
    return (
        None,
        None,
        None,
        None,
        "STAFF_KRB_NAME@MIT.EDU",
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
        "STUDENT_KRB_NAME@MIT.EDU",
        None,
        None,
        None,
    )


@pytest.fixture()
def staff_patron_all_values_record():
    return (
        "Doe, Jane",
        "AA-B1-11",
        "5555555555",
        "222222222",
        "STAFF_KRB_NAME@MIT.EDU",
        datetime.datetime(2023, 6, 30, 0, 0),
        "STAFF_KRB_NAME",
        "27",
        "Staff - Lincoln Labs",
        "10000948",
        "LL-Homeland Protection & Air Traffic Con",
        "Part-time Flexible/LL",
        "Part-time Flexible/LL",
        "33333333333333",
    )


@pytest.fixture()
def student_patron_all_values_record():
    return (
        "111111111",
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
        "STUDENT_KRB_NAME@MIT.EDU",
        "STUDENT_KRB_NAME",
        "1",
        "11111111111111",
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
