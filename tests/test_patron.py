from bs4 import BeautifulSoup
from freezegun import freeze_time

from patronload.patron import (
    format_phone_number,
    patron_xml_from_records,
    populate_patron_common_fields,
)

SIX_MONTHS = "2023-09-01Z"
TWO_YEARS = "2025-09-01Z"


def test_format_phone_number_valid_value_succeeds():
    assert format_phone_number("1111111111") == "111-111-1111"


def test_format_phone_number_invalid_value_is_returned():
    assert format_phone_number("abcd") == "abcd"


@freeze_time("2023-03-01")
def test_patron_xml_from_records_staff_success(staff_patron_all_values_record):
    with open(
        "tests/fixtures/staff_patron_xml_record.xml", "r", encoding="utf8"
    ) as xml_file:
        patron_xml_record = next(
            patron_xml_from_records("staff", [staff_patron_all_values_record])
        )
        assert patron_xml_record == BeautifulSoup(
            xml_file.read(),
            features="xml",
        )


@freeze_time("2023-03-01")
def test_patron_xml_from_records_student_success(
    student_patron_all_values_record,
):
    with open(
        "tests/fixtures/student_patron_xml_record.xml", "r", encoding="utf8"
    ) as xml_file:
        patron_xml_record = next(
            patron_xml_from_records("student", [student_patron_all_values_record])
        )
        assert patron_xml_record == BeautifulSoup(
            xml_file.read(),
            features="xml",
        )


def test_populate_patron_common_fields_staff_all_values_success(
    staff_patron_template, staff_patron_all_values_record
):
    patron_xml_record = populate_patron_common_fields(
        staff_patron_template,
        staff_patron_all_values_record,
        SIX_MONTHS,
        TWO_YEARS,
    )
    assert patron_xml_record.primary_id.string == "STAFF_KRB_NAME@MIT.EDU"
    assert patron_xml_record.expiry_date.string == "2023-09-01Z"
    assert patron_xml_record.purge_date.string == "2025-09-01Z"
    assert (
        patron_xml_record.emails.email.email_address.string == "STAFF_KRB_NAME@MIT.EDU"
    )
    assert (
        patron_xml_record.user_identifiers.user_identifier.value.string == "222222222"
    )
    assert (
        patron_xml_record.find_all("user_identifier")[1].value.string
        == "22222222222222"
    )


def test_populate_patron_common_fields_staff_no_krb_name_but_email_success(
    staff_patron_template,
):
    staff_patron_record_no_krb_but_email = (
        "222222222",
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
        None,
        None,
        None,
    )
    patron_xml_record = populate_patron_common_fields(
        staff_patron_template,
        staff_patron_record_no_krb_but_email,
        SIX_MONTHS,
        TWO_YEARS,
    )
    assert patron_xml_record.primary_id.string == "STAFF_KRB_NAME@MIT.EDU"
    assert patron_xml_record.expiry_date.string == "2023-09-01Z"
    assert patron_xml_record.purge_date.string == "2025-09-01Z"
    assert (
        patron_xml_record.emails.email.email_address.string == "STAFF_KRB_NAME@MIT.EDU"
    )
    assert (
        patron_xml_record.user_identifiers.user_identifier.value.string == "222222222"
    )


def test_populate_patron_common_fields_staff_null_values_success(
    staff_patron_template, staff_patron_null_values_record
):
    patron_xml_record = populate_patron_common_fields(
        staff_patron_template,
        staff_patron_null_values_record,
        SIX_MONTHS,
        TWO_YEARS,
    )
    assert patron_xml_record.expiry_date.string == "2023-09-01Z"
    assert patron_xml_record.purge_date.string == "2025-09-01Z"
    assert (
        patron_xml_record.user_identifiers.user_identifier.value.string == "222222222"
    )
    assert not list(list(patron_xml_record.emails.children))
    assert len(list(patron_xml_record.find_all("user_identifier"))) == 1


def test_populate_patron_common_fields_student_all_values_success(
    student_patron_template, student_patron_all_values_record
):
    patron_xml_record = populate_patron_common_fields(
        student_patron_template,
        student_patron_all_values_record,
        SIX_MONTHS,
        TWO_YEARS,
    )
    assert patron_xml_record.primary_id.string == "STUDENT_KRB_NAME@MIT.EDU"
    assert patron_xml_record.expiry_date.string == "2023-09-01Z"
    assert patron_xml_record.purge_date.string == "2025-09-01Z"
    assert (
        patron_xml_record.emails.email.email_address.string
        == "STUDENT_KRB_NAME@MIT.EDU"
    )
    assert (
        patron_xml_record.user_identifiers.user_identifier.value.string == "111111111"
    )
    assert (
        patron_xml_record.find_all("user_identifier")[1].value.string
        == "11111111111111"
    )


def test_populate_patron_common_fields_student_no_krb_name_success(
    student_patron_template,
):
    student_patron_no_krb_but_email = (
        "111111111",
        "STUDENT_KRB_NAME@MIT.EDU",
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
    patron_xml_record = populate_patron_common_fields(
        student_patron_template,
        student_patron_no_krb_but_email,
        SIX_MONTHS,
        TWO_YEARS,
    )
    assert patron_xml_record.primary_id.string == "STUDENT_KRB_NAME@MIT.EDU"
    assert patron_xml_record.expiry_date.string == "2023-09-01Z"
    assert patron_xml_record.purge_date.string == "2025-09-01Z"
    assert (
        patron_xml_record.emails.email.email_address.string
        == "STUDENT_KRB_NAME@MIT.EDU"
    )
    assert (
        patron_xml_record.user_identifiers.user_identifier.value.string == "111111111"
    )


def test_populate_patron_common_fields_student_null_values_success(
    student_patron_template, student_patron_null_values_record
):
    patron_xml_record = populate_patron_common_fields(
        student_patron_template,
        student_patron_null_values_record,
        SIX_MONTHS,
        TWO_YEARS,
    )
    assert patron_xml_record.expiry_date.string == "2023-09-01Z"
    assert patron_xml_record.purge_date.string == "2025-09-01Z"
    assert (
        patron_xml_record.user_identifiers.user_identifier.value.string == "111111111"
    )
    assert not list(list(patron_xml_record.emails.children))
    assert len(list(patron_xml_record.find_all("user_identifier"))) == 1
