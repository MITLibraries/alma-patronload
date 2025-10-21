import logging
from io import BytesIO
from zipfile import ZipFile

from bs4 import BeautifulSoup
from freezegun import freeze_time

from patronload.patron import (
    create_and_write_to_zip_file_in_memory,
    format_phone_number,
    patrons_xml_string_from_records,
    populate_common_fields,
    populate_staff_fields,
    populate_student_fields,
)

SIX_MONTHS = "2023-09-01Z"
TWO_YEARS = "2025-09-01Z"


def test_create_and_write_to_zip_file_in_memory_success():
    zip_file_object = create_and_write_to_zip_file_in_memory("test.xml", "<xml></xml>")
    with ZipFile(BytesIO(zip_file_object.getvalue()), "r") as zip_file:
        assert zip_file.namelist() == ["test.xml"]


def test_format_phone_number_valid_value_success():
    assert format_phone_number("1111111111") == "111-111-1111"


def test_format_phone_number_invalid_value_is_returned():
    assert format_phone_number("abcd") == "abcd"


@freeze_time("2023-03-01 12:00:00")
def test_patrons_xml_string_from_records_staff_success(
    caplog,
    staff_database_record_with_null_values,
    staff_database_record_with_all_values,
    staff_database_record_krb_and_null_values,
    staff_patrons_xml,
):
    caplog.set_level(logging.DEBUG)
    results = patrons_xml_string_from_records(
        "staff",
        [
            staff_database_record_with_null_values,
            staff_database_record_with_all_values,
            staff_database_record_krb_and_null_values,
            staff_database_record_with_all_values,
        ],
        [],
    )
    assert (
        BeautifulSoup(results, features="xml").prettify() == staff_patrons_xml.prettify()
    )
    assert (
        "Rejected record: MIT ID # '222222222', missing field KRB_NAME_UPPERCASE"
    ) in caplog.text
    assert (
        "Patron record has already been created for MIT ID # '444444444'"
    ) in caplog.text


@freeze_time("2023-03-01 12:00:00")
def test_patrons_xml_string_from_records_student_success(
    caplog,
    student_database_record_with_null_values,
    student_database_record_with_all_values,
    student_database_record_krb_and_null_values,
    student_patrons_xml,
):
    caplog.set_level(logging.DEBUG)
    results = patrons_xml_string_from_records(
        "student",
        [
            student_database_record_with_null_values,
            student_database_record_with_all_values,
            student_database_record_krb_and_null_values,
            student_database_record_with_all_values,
        ],
        [],
    )
    assert (
        BeautifulSoup(results, features="xml").prettify()
        == student_patrons_xml.prettify()
    )
    assert (
        "Rejected record: MIT ID # '111111111', missing field KRB_NAME_UPPERCASE"
        in caplog.text
    )
    assert (
        "Patron record has already been created for MIT ID # '333333333'"
    ) in caplog.text


def test_populate_common_fields_staff_all_values_success(
    staff_patron_template, staff_patron_all_values_dict
):
    patron_xml_record = populate_common_fields(
        staff_patron_template,
        staff_patron_all_values_dict,
        SIX_MONTHS,
        TWO_YEARS,
    )
    assert patron_xml_record.pref_first_name.string == "Nancy-preferred"
    assert (
        patron_xml_record.pref_middle_name.string == ""
    )  # staff fixture has no preferred middle name
    assert patron_xml_record.pref_last_name.string == "Drew-preferred"
    assert patron_xml_record.first_name.string == "Nancy"
    assert (
        patron_xml_record.middle_name.string == ""
    )  # staff fixture has no legal middle name
    assert patron_xml_record.last_name.string == "Drew"
    assert patron_xml_record.primary_id.string == "STAFF_KRB_NAME@MIT.EDU"
    assert patron_xml_record.expiry_date.string == "2023-09-01Z"
    assert patron_xml_record.purge_date.string == "2025-09-01Z"
    assert patron_xml_record.emails.email.email_address.string == "STAFF_KRB_NAME@MIT.EDU"
    assert patron_xml_record.find_all("user_identifier")[0].value.string == "222222222"
    assert (
        patron_xml_record.find_all("user_identifier")[1].value.string == "22222222222222"
    )


def test_populate_common_fields_staff_null_values_success(
    staff_patron_template, staff_patron_all_values_dict
):
    for key in [
        k
        for k in staff_patron_all_values_dict
        if k not in ["MIT_ID", "KRB_NAME_UPPERCASE"]
    ]:
        staff_patron_all_values_dict[key] = None
    patron_xml_record = populate_common_fields(
        staff_patron_template,
        staff_patron_all_values_dict,
        SIX_MONTHS,
        TWO_YEARS,
    )
    assert patron_xml_record.expiry_date.string == "2023-09-01Z"
    assert patron_xml_record.purge_date.string == "2025-09-01Z"
    assert patron_xml_record.user_identifiers.user_identifier.value.string == "222222222"
    assert not list(patron_xml_record.emails.children)
    assert len(list(patron_xml_record.find_all("user_identifier"))) == 1


def test_populate_common_fields_student_all_values_success(
    student_patron_template, student_patron_all_values_dict
):
    patron_xml_record = populate_common_fields(
        student_patron_template,
        student_patron_all_values_dict,
        SIX_MONTHS,
        TWO_YEARS,
    )
    assert patron_xml_record.pref_first_name.string == "Jane-preferred"
    assert patron_xml_record.pref_middle_name.string == "Janeth-preferred"
    assert patron_xml_record.pref_last_name.string == "Doe-preferred"
    assert patron_xml_record.first_name.string == "Jane"
    assert patron_xml_record.middle_name.string == "Janeth"
    assert patron_xml_record.last_name.string == "Doe"
    assert patron_xml_record.primary_id.string == "STUDENT_KRB_NAME@MIT.EDU"
    assert patron_xml_record.expiry_date.string == "2023-09-01Z"
    assert patron_xml_record.purge_date.string == "2025-09-01Z"
    assert (
        patron_xml_record.emails.email.email_address.string == "STUDENT_KRB_NAME@MIT.EDU"
    )
    assert patron_xml_record.find_all("user_identifier")[0].value.string == "111111111"
    assert (
        patron_xml_record.find_all("user_identifier")[1].value.string == "11111111111111"
    )


def test_populate_common_fields_student_null_values_success(
    student_patron_template, student_patron_all_values_dict
):
    for key in [
        k
        for k in student_patron_all_values_dict
        if k not in ["MIT_ID", "KRB_NAME_UPPERCASE"]
    ]:
        student_patron_all_values_dict[key] = None
    patron_xml_record = populate_common_fields(
        student_patron_template,
        student_patron_all_values_dict,
        SIX_MONTHS,
        TWO_YEARS,
    )
    assert patron_xml_record.expiry_date.string == "2023-09-01Z"
    assert patron_xml_record.purge_date.string == "2025-09-01Z"
    assert patron_xml_record.user_identifiers.user_identifier.value.string == "111111111"
    assert not list(patron_xml_record.emails.children)
    assert len(list(patron_xml_record.find_all("user_identifier"))) == 1


def test_populate_staff_fields_all_values_success(
    staff_patron_template, staff_patron_all_values_dict
):
    patron_xml_record = populate_staff_fields(
        staff_patron_template,
        staff_patron_all_values_dict,
    )

    assert patron_xml_record.user_group.string == "27"
    assert patron_xml_record.user_group["desc"] == "Staff - Lincoln Labs"
    assert patron_xml_record.line1.string == "AA-B1-11"
    assert patron_xml_record.phone_number.string == "555-555-5555"
    assert patron_xml_record.statistic_category.string == "NK"
    assert (
        patron_xml_record.statistic_category["desc"]
        == "LL-Homeland Protection & Air Traffic Con"
    )


def test_populate_staff_fields_null_values_success(
    staff_patron_template, staff_patron_all_values_dict
):
    for key in [k for k in staff_patron_all_values_dict if k != "MIT_ID"]:
        staff_patron_all_values_dict[key] = None
    patron_xml_record = populate_staff_fields(
        staff_patron_template,
        staff_patron_all_values_dict,
    )
    assert patron_xml_record.user_group.string == ""
    assert patron_xml_record.user_group["desc"] == ""
    assert patron_xml_record.line1.string == "NO ADDRESS ON FILE IN DATA WAREHOUSE"
    assert patron_xml_record.phones.is_empty_element
    assert patron_xml_record.statistic_category.string == "ZQ"
    assert patron_xml_record.statistic_category["desc"] == "Unknown"


def test_populate_student_fields_all_values_success(
    student_patron_template, student_patron_all_values_dict
):
    patron_xml_record = populate_student_fields(
        student_patron_template,
        student_patron_all_values_dict,
    )

    assert patron_xml_record.address.line1.string == "100 Smith St"
    assert patron_xml_record.line3.string == "Apt 34"
    assert patron_xml_record.city.string == "Cambridge"
    assert patron_xml_record.state_province.string == "MA"
    assert patron_xml_record.postal_code.string == "00000"
    assert patron_xml_record.find_all("phone_number")[0].string == "333-333-3333"
    assert patron_xml_record.find_all("phone_number")[1].string == "555-555-5555"
    assert patron_xml_record.statistic_category.string == "SN"
    assert patron_xml_record.user_group.string == "32"


def test_populate_student_fields_null_values_success(
    student_patron_template, student_patron_all_values_dict
):
    for key in [k for k in student_patron_all_values_dict if k != "MIT_ID"]:
        student_patron_all_values_dict[key] = None
    patron_xml_record = populate_student_fields(
        student_patron_template,
        student_patron_all_values_dict,
    )

    assert (
        patron_xml_record.address.line1.string == "NO ADDRESS ON FILE IN DATA WAREHOUSE"
    )
    assert patron_xml_record.line3.string == ""
    assert patron_xml_record.city.string == ""
    assert patron_xml_record.state_province.string == ""
    assert patron_xml_record.postal_code.string == ""
    assert patron_xml_record.find_all("phone") == []
    assert patron_xml_record.statistic_category.string == "ZZ"
    assert patron_xml_record.user_group.string is None


def test_populate_student_fields_no_office_phone_success(
    student_patron_template, student_patron_all_values_dict
):
    student_patron_all_values_dict["OFFICE_PHONE"] = None
    patron_xml_record = populate_student_fields(
        student_patron_template,
        student_patron_all_values_dict,
    )
    assert patron_xml_record.phone_number.string == "555-555-5555"
    assert len(list(patron_xml_record.find_all("phone_number"))) == 1


def test_populate_student_fields_no_office_phone_no_term_phone1_success(
    student_patron_template, student_patron_all_values_dict
):
    student_patron_all_values_dict["OFFICE_PHONE"] = None
    student_patron_all_values_dict["TERM_PHONE1"] = None
    patron_xml_record = populate_student_fields(
        student_patron_template,
        student_patron_all_values_dict,
    )
    assert patron_xml_record.phone_number.string == "444-444-4444"
    assert len(list(patron_xml_record.find_all("phone_number"))) == 1


def test_populate_student_fields_undergraduate_user_group_success(
    student_patron_template, student_patron_all_values_dict
):
    student_patron_all_values_dict["STUDENT_YEAR"] = "1"
    patron_xml_record = populate_student_fields(
        student_patron_template,
        student_patron_all_values_dict,
    )
    assert patron_xml_record.user_group.string == "31"


def test_populate_student_fields_non_mit_user_group_success(
    student_patron_template, student_patron_all_values_dict
):
    student_patron_all_values_dict["HOME_DEPARTMENT"] = "NIV"
    patron_xml_record = populate_student_fields(
        student_patron_template,
        student_patron_all_values_dict,
    )
    assert patron_xml_record.user_group.string == "54"
