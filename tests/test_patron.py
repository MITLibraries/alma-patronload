from freezegun import freeze_time

from patronload.config import STAFF_FIELDS, STUDENT_FIELDS
from patronload.patron import (
    create_patron_dicts,
    format_phone_number,
    patron_xml_records_from_dicts,
    populate_patron_common_fields,
)


def test_create_patron_dicts_staff(
    staff_patron_all_values_record, staff_patron_all_values_dict
):
    patron_dict = create_patron_dicts(STAFF_FIELDS, [staff_patron_all_values_record])
    assert next(patron_dict) == staff_patron_all_values_dict


def test_create_patron_dicts_staff_null_values_transform_correctly(
    staff_patron_null_values_record, staff_patron_null_values_dict
):
    patron_dict = create_patron_dicts(STAFF_FIELDS, [staff_patron_null_values_record])
    assert next(patron_dict) == staff_patron_null_values_dict


def test_create_patron_dicts_student(
    student_patron_all_values_record, student_patron_all_values_dict
):
    patron_dict = create_patron_dicts(
        STUDENT_FIELDS, [student_patron_all_values_record]
    )
    assert next(patron_dict) == student_patron_all_values_dict


def test_create_patron_dicts_student_null_values_transform_correctly(
    student_patron_null_values_record, student_patron_null_values_dict
):
    patron_dict = create_patron_dicts(
        STUDENT_FIELDS, [student_patron_null_values_record]
    )
    assert next(patron_dict) == student_patron_null_values_dict


def test_format_phone_number_valid_value_succeeds():
    assert format_phone_number("1111111111") == "111-111-1111"


def test_format_phone_number_invalid_value_is_returned():
    assert format_phone_number("abcd") == "abcd"


@freeze_time("2023-03-01")
def test_patron_xml_records_from_dicts_staff_success(staff_patron_all_values_dict):
    patron_xml_record = next(
        patron_xml_records_from_dicts("staff", [staff_patron_all_values_dict])
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


@freeze_time("2023-03-01")
def test_patron_xml_records_from_dicts_student_success(student_patron_all_values_dict):
    patron_xml_record = next(
        patron_xml_records_from_dicts("student", [student_patron_all_values_dict])
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


@freeze_time("2023-03-01")
def test_populate_patron_common_fields_staff_all_values_success(
    staff_patron_template, staff_patron_all_values_dict
):
    patron_xml_record = populate_patron_common_fields(
        staff_patron_template, staff_patron_all_values_dict
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


@freeze_time("2023-03-01")
def test_populate_patron_common_fields_staff_null_values_success(
    staff_patron_template, staff_patron_null_values_dict
):
    patron_xml_record = populate_patron_common_fields(
        staff_patron_template, staff_patron_null_values_dict
    )
    assert patron_xml_record.primary_id.string == "STAFF_KRB_NAME@MIT.EDU"
    assert patron_xml_record.expiry_date.string == "2023-09-01Z"
    assert patron_xml_record.purge_date.string == "2025-09-01Z"
    assert (
        patron_xml_record.emails.email.email_address.string == "STAFF_KRB_NAME@MIT.EDU"
    )
    assert patron_xml_record.user_identifiers.user_identifier.value.string == ""


@freeze_time("2023-03-01")
def test_populate_patron_common_fields_student_all_values_success(
    student_patron_template, student_patron_all_values_dict
):
    patron_xml_record = populate_patron_common_fields(
        student_patron_template, student_patron_all_values_dict
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


@freeze_time("2023-03-01")
def test_populate_patron_common_fields_student_null_values_success(
    student_patron_template, student_patron_null_values_dict
):
    patron_xml_record = populate_patron_common_fields(
        student_patron_template, student_patron_null_values_dict
    )
    assert patron_xml_record.primary_id.string == "STUDENT_KRB_NAME@MIT.EDU"
    assert patron_xml_record.expiry_date.string == "2023-09-01Z"
    assert patron_xml_record.purge_date.string == "2025-09-01Z"
    assert (
        patron_xml_record.emails.email.email_address.string
        == "STUDENT_KRB_NAME@MIT.EDU"
    )
    assert patron_xml_record.user_identifiers.user_identifier.value.string == ""
