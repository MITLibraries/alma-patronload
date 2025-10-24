import datetime
import logging
import re
from copy import deepcopy
from io import BytesIO
from typing import Any
from zipfile import ZipFile

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

from patronload.config import (
    STAFF_DEPARTMENTS,
    STAFF_FIELDS,
    STUDENT_DEPARTMENTS,
    STUDENT_FIELDS,
)

logger = logging.getLogger(__name__)


def patrons_xml_string_from_records(
    patron_type: str, patron_records: list[tuple], existing_krb_names: list[str]
) -> str:
    """Create patrons XML string from patron records.

    Args:
        patron_type: The type of patron record being processed, staff or student.
        patron_records: A list of patron record tuples.
        existing_krb_names: A list of IDs that have already been processed. Used to ensure
        that duplicate profiles are not created, such as when students have already been
        added as staff.
    """
    patrons_xml_string = '<?xml version="1.0" encoding="utf-8"?><userRecords>'

    with open(f"config/{patron_type}_template.xml", encoding="utf8") as xml_template:
        patron_template = BeautifulSoup(xml_template, "html.parser")
        six_months = (
            datetime.datetime.now(tz=datetime.UTC).date() + relativedelta(months=+6)
        ).strftime("%Y-%m-%d") + "Z"
        two_years = (
            datetime.datetime.now(tz=datetime.UTC).date()
            + relativedelta(years=+2, months=+6)
        ).strftime("%Y-%m-%d") + "Z"

        for patron_record in patron_records:
            if patron_record[2]:  # Check for KRB_NAME_UPPERCASE field
                if patron_record[2] not in existing_krb_names:
                    existing_krb_names.append(patron_record[2])
                    template = deepcopy(patron_template)
                    if patron_type == "staff":
                        patron_dict = dict(zip(STAFF_FIELDS, patron_record, strict=True))
                        updated_template = populate_staff_fields(template, patron_dict)
                    elif patron_type == "student":
                        patron_dict = dict(
                            zip(STUDENT_FIELDS, patron_record, strict=True)
                        )
                        updated_template = populate_student_fields(template, patron_dict)
                    patron_xml = populate_common_fields(
                        updated_template,
                        patron_dict,
                        six_months,
                        two_years,
                    )
                    patrons_xml_string += patron_xml.decode_contents()
                else:
                    logger.debug(
                        "Patron record has already been created for MIT ID # '%s'",
                        patron_record[0],
                    )
            else:
                logger.debug(
                    "Rejected record: MIT ID # '%s', missing field KRB_NAME_UPPERCASE",
                    patron_record[0],
                )
    patrons_xml_string += "</userRecords>"
    return patrons_xml_string


def populate_staff_fields(
    patron_template: BeautifulSoup,
    patron_dict: dict[str, Any],
) -> BeautifulSoup:
    """Populate the staff fields in a patron record.

    The order of the patron record fields must be in same order as they in the
    STAFF_FIELDS value list.

    Args:
        patron_template: An XML template for a patron record
        patron_dict: A dict of patron record values.
    """
    patron_template.user_group.string = (  # type: ignore[union-attr]
        patron_dict["LIBRARY_PERSON_TYPE_CODE"] or ""
    )
    patron_template.user_group["desc"] = (  # type: ignore[index,union-attr]
        patron_dict["LIBRARY_PERSON_TYPE"] or ""
    )

    patron_template.address.line1.string = (  # type: ignore[union-attr]
        patron_dict["OFFICE_ADDRESS"]
        if patron_dict["OFFICE_ADDRESS"]
        else "NO ADDRESS ON FILE IN DATA WAREHOUSE"
    )
    if patron_dict["OFFICE_PHONE"]:
        patron_template.phone_number.string = (  # type: ignore[union-attr]
            format_phone_number(
                patron_dict["OFFICE_PHONE"],
            )
        )
    else:
        patron_template.phones.clear()  # type: ignore[union-attr]

    if patron_dict["ORG_UNIT_ID"] in STAFF_DEPARTMENTS:
        patron_template.statistic_category.string = (  # type: ignore[union-attr]
            STAFF_DEPARTMENTS[patron_dict["ORG_UNIT_ID"]]
        )
    else:
        patron_template.statistic_category.string = "ZQ"  # type: ignore[union-attr]
        logger.debug(
            "Unknown dept: '%s' in record with MIT ID # '%s'",
            patron_dict["ORG_UNIT_ID"],
            patron_dict["MIT_ID"],
        )
    patron_template.statistic_category["desc"] = (  # type: ignore[index,union-attr]
        patron_dict["ORG_UNIT_TITLE"] or "Unknown"
    )
    return patron_template


def populate_student_fields(
    patron_template: BeautifulSoup,
    patron_dict: dict[str, Any],
) -> BeautifulSoup:
    """Populate the student fields in a patron record.

    The order of the patron record fields must be in same order as they in the
    STUDENT_FIELDS value list.

    Args:
        patron_template: An XML template for a patron record
        patron_dict: A dict of patron record values.
    """
    patron_template.address.line1.string = (  # type: ignore[union-attr]
        patron_dict["TERM_STREET1"]
        if patron_dict["TERM_STREET1"]
        else "NO ADDRESS ON FILE IN DATA WAREHOUSE"
    )
    patron_template.address.line3.string = (  # type: ignore[union-attr]
        patron_dict["TERM_STREET2"] or ""
    )
    patron_template.address.city.string = (  # type: ignore[union-attr]
        patron_dict["TERM_CITY"] or ""
    )
    patron_template.address.state_province.string = (  # type: ignore[union-attr]
        patron_dict["TERM_STATE"] or ""
    )
    patron_template.address.postal_code.string = (  # type: ignore[union-attr]
        patron_dict["TERM_ZIP"] or ""
    )

    preferred_phone_number = patron_template.find_all("phone_number")[0]
    preferred_phone_number.string = format_phone_number(
        patron_dict["OFFICE_PHONE"]
        or patron_dict["TERM_PHONE1"]
        or patron_dict["TERM_PHONE2"]
        or ""
    )
    if patron_dict["OFFICE_PHONE"]:
        other_phone_number = patron_template.find_all("phone_number")[1]
        other_phone_number.string = format_phone_number(patron_dict["TERM_PHONE1"] or "")
    for phone in patron_template.find_all("phone"):
        if not phone.phone_number.string:
            phone.extract()
    if patron_dict["HOME_DEPARTMENT"] in STUDENT_DEPARTMENTS:
        patron_template.statistic_category.string = (  # type: ignore[union-attr]
            STUDENT_DEPARTMENTS[patron_dict["HOME_DEPARTMENT"]]
        )
    else:
        patron_template.statistic_category.string = "ZZ"  # type: ignore[union-attr]
        logger.debug(
            "Unknown dept: '%s' in record with MIT ID # '%s'",
            patron_dict["HOME_DEPARTMENT"],
            patron_dict["MIT_ID"],
        )

    # User Group codes
    # 31 = Student - Undergraduate
    # 32 = Student - Graduate
    # 54 = Non-MIT - Cross-registered
    if patron_dict["STUDENT_YEAR"]:
        if re.search("^[1234Uu]$", patron_dict["STUDENT_YEAR"]):
            patron_template.user_group.string = "31"  # type: ignore[union-attr]
        elif re.search("^[Gg]$", patron_dict["STUDENT_YEAR"]):
            patron_template.user_group.string = "32"  # type: ignore[union-attr]
    if patron_dict["HOME_DEPARTMENT"] and re.search(
        "^NI[UVWTRH]$", patron_dict["HOME_DEPARTMENT"]
    ):
        patron_template.user_group.string = "54"  # type: ignore[union-attr]
    return patron_template


def populate_common_fields(
    patron_template: BeautifulSoup,
    patron_dict: dict[str, Any],
    six_months: str,
    two_years: str,
) -> BeautifulSoup:
    """Populate the fields common to both staff and student patron records.

    The order of the patron record fields must be in same order as they in the
    STAFF_FIELDS and STUDENT_FIELDS value lists.

    Args:
        patron_template: An XML template for a patron record
        patron_dict: A dict of patron record values.
        six_months: Six months from the current date.
        two_years: Two years from the current date.
    """
    for part in ["FIRST", "MIDDLE", "LAST"]:
        pref = (patron_dict.get(f"PREFERRED_{part}_NAME") or "").strip()
        legal = (patron_dict.get(f"LEGAL_{part}_NAME") or "").strip()

        # Assign legal name
        getattr(patron_template, f"{part.lower()}_name").string = legal

        # Compare case-insensitively; assign only if different
        getattr(patron_template, f"pref_{part.lower()}_name").string = (
            pref if pref.lower() != legal.lower() and pref else ""
        )
    patron_template.primary_id.string = (  # type: ignore[union-attr]
        patron_dict["KRB_NAME_UPPERCASE"] + "@MIT.EDU"
    )
    patron_template.expiry_date.string = six_months  # type: ignore[union-attr]
    patron_template.purge_date.string = two_years  # type: ignore[union-attr]

    if patron_dict["EMAIL_ADDRESS"]:
        patron_template.email_address.string = patron_dict[  # type: ignore[union-attr]
            "EMAIL_ADDRESS"
        ]
    else:
        patron_template.emails.clear()  # type: ignore[union-attr]

    for user_identifier in patron_template.find_all("user_identifier"):
        if user_identifier.find("id_type", desc="MIT ID"):
            user_identifier.value.string = patron_dict["MIT_ID"] or ""
        elif user_identifier.find("id_type", desc="Barcode"):
            if patron_dict["LIBRARY_ID"] and patron_dict["LIBRARY_ID"] != "NONE":
                user_identifier.value.string = patron_dict["LIBRARY_ID"]
            else:
                user_identifier.decompose()
    return patron_template


def create_and_write_to_zip_file_in_memory(
    xml_file_name: str, file_content: str
) -> BytesIO:
    """Create zip file in memory and zip a string value.

    Used to zip patron XML data before uploading to S3 bucket.

    Args:
        xml_file_name: The name of the XML file to be zipped.
        file_content: The file content to be zipped, must be a str.
    """
    zip_file_object = BytesIO()
    with ZipFile(zip_file_object, "w") as zip_file:
        zip_file.writestr(
            xml_file_name,
            file_content,
        )
        return zip_file_object


def format_phone_number(phone_number: str) -> str:
    """Format a string of 10 numbers as a phone number with dashes.

    Args:
        phone_number: A string that may contain a phone number.
    """
    return re.sub(r"(\d{3})(\d{3})(\d{4})", r"\1-\2-\3", phone_number)
