import logging
import re
from copy import deepcopy
from datetime import date
from typing import Any, Generator

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

from patronload.config import STAFF_FIELDS, STUDENT_FIELDS

logger = logging.getLogger(__name__)


def format_phone_number(phone_number: str) -> str:
    """
    Format a string of 10 numbers as a phone number with dashes.

    Args:
        phone_number: A string that may contain a phone number.
    """
    return re.sub(r"(\d{3})(\d{3})(\d{4})", r"\1-\2-\3", phone_number)


def populate_patron_common_fields(
    patron_template: BeautifulSoup,
    patron_dict: dict[str, Any],
    six_months: str,
    two_years: str,
) -> BeautifulSoup:
    """
    Populate the fields common to both staff and student patron records.

    The order of the patron record fields must be in same order as they in the
    STAFF_FIELDS and STUDENT_FIELDS value lists.

    Args:
        patron: An XML template for a patron record
        patron_dict: A dict of patron record values.
    """
    patron = deepcopy(patron_template)
    patron.primary_id.string = (  # type: ignore[union-attr]
        patron_dict["KRB_NAME_UPPERCASE"] + "@MIT.EDU"
    )
    patron.expiry_date.string = six_months  # type: ignore[union-attr]
    patron.purge_date.string = two_years  # type: ignore[union-attr]

    if patron_dict["EMAIL_ADDRESS"]:
        patron.email_address.string = patron_dict[  # type: ignore[union-attr]
            "EMAIL_ADDRESS"
        ]
    else:
        patron.emails.clear()  # type: ignore[union-attr]

    for user_identifier in patron.find_all("user_identifier"):
        if user_identifier.find("id_type", desc="Additional"):
            user_identifier.value.string = patron_dict["MIT_ID"] or ""
        elif user_identifier.find("id_type", desc="Barcode"):
            if patron_dict["LIBRARY_ID"] and patron_dict["LIBRARY_ID"] != "NONE":
                user_identifier.value.string = patron_dict["LIBRARY_ID"]
            else:
                user_identifier.decompose()
    return patron


def patron_xml_from_records(
    patron_type: str, patron_records: list[tuple]
) -> Generator[BeautifulSoup, None, None]:
    """
    Create patron XML records from patron records.

    Args:
        patron_type: The type of patron record being processed, staff or student.
        patron_records: A list of patron record tuples.
    """
    with open(
        f"config/{patron_type}_template.xml", "r", encoding="utf8"
    ) as xml_template:
        patron_template = BeautifulSoup(xml_template, features="xml")
        six_months = (date.today() + relativedelta(months=+6)).strftime(
            "%Y-%m-%d"
        ) + "Z"
        two_years = (date.today() + relativedelta(years=+2, months=+6)).strftime(
            "%Y-%m-%d"
        ) + "Z"

        for patron_record in patron_records:
            if patron_record[2]:  # Check for KRB_NAME_UPPERCASE field
                template = deepcopy(patron_template)
                if patron_type == "staff":
                    patron_dict = dict(zip(STAFF_FIELDS, patron_record))
                elif patron_type == "student":
                    patron_dict = dict(zip(STUDENT_FIELDS, patron_record))
                patron_xml = populate_patron_common_fields(
                    template,
                    patron_dict,
                    six_months,
                    two_years,
                )
                yield patron_xml
            else:
                logger.error(
                    "Rejecting record # '%s' as it is missing field KRB_NAME_UPPERCASE",
                    patron_record[0],
                )
                continue
