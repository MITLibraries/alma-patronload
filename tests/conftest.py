import datetime
import os

import boto3
import pytest
from bs4 import BeautifulSoup
from click.testing import CliRunner
from moto import mock_s3


@pytest.fixture(name="credentials")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(name="config_values")
def config_values_fixture():
    config_values = {
        "DATAWAREHOUSE_CLOUDCONNECTOR_JSON": (
            '{"USER": "user123",  "PASSWORD": "pass123", "HOST": "http://localhost", '
            '"PORT": "1234", "PATH": "database5678"}'
        ),
        "LOG_LEVEL": "INFO",
        "S3_BUCKET_NAME": "test-bucket",
        "S3_PATH": "patronload",
        "WORKSPACE": "test",
    }
    return config_values


@pytest.fixture()
def mocked_s3(credentials):  # pylint: disable=W0613
    with mock_s3():
        s3_instance = boto3.client("s3", region_name="us-east-1")
        s3_instance.create_bucket(Bucket="test-bucket")
        s3_instance.put_object(
            Body="",
            Bucket="test-bucket",
            Key="patronload/1.zip",
        )
        s3_instance.put_object(
            Body="",
            Bucket="test-bucket",
            Key="2.zip",
        )
        yield s3_instance


@pytest.fixture()
def s3_client():
    return boto3.client("s3", region_name="us-east-1")


@pytest.fixture()
def staff_database_record_with_all_values():
    return (
        "444444444",
        "STAFF_KRB_NAME@MIT.EDU",
        "STAFF_KRB_NAME",
        "44444444444444",
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
def staff_database_record_krb_and_null_values():
    return (
        "666666666",
        None,
        "2STAFF_KRB_NAME",
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
def staff_database_record_with_null_values():
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
        "LIBRARY_ID": "22222222222222",
    }


@pytest.fixture()
def student_database_record_with_all_values():
    return (
        "333333333",
        "STUDENT_KRB_NAME@MIT.EDU",
        "STUDENT_KRB_NAME",
        "33333333333333",
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
def student_database_record_krb_and_null_values():
    return (
        "555555555",
        None,
        "2STUDENT_KRB_NAME",
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
def student_database_record_with_null_values():
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
def staff_patron_template():
    with open("config/staff_template.xml", "r", encoding="utf8") as xml_template:
        return BeautifulSoup(xml_template, features="xml")


@pytest.fixture()
def staff_patrons_xml():
    with open("tests/fixtures/staff_patrons.xml", "r", encoding="utf8") as patrons_xml:
        return BeautifulSoup(patrons_xml, features="xml")


@pytest.fixture()
def student_patron_template():
    with open("config/student_template.xml", "r", encoding="utf8") as xml_template:
        return BeautifulSoup(xml_template, features="xml")


@pytest.fixture()
def student_patrons_xml():
    with open(
        "tests/fixtures/student_patrons.xml", "r", encoding="utf8"
    ) as patrons_xml:
        return BeautifulSoup(patrons_xml, features="xml")


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture(autouse=True)
def test_env(config_values):
    os.environ = config_values
    yield
