import logging
import re
from datetime import date
from typing import Generator

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

from patronload.config import COMMON_FIELDS

logger = logging.getLogger(__name__)


def format_phone_number(phone_number: str) -> str:
    """
    Format a string of 10 numbers as a phone number with dashes.

    Args:
        phone_number: A string that may contain a phone number.
    """
    return re.sub(r"(\d{3})(\d{3})(\d{4})", r"\1-\2-\3", phone_number)


def populate_patron_common_fields(
    patron: BeautifulSoup, patron_record: tuple, six_months: str, two_years: str
) -> BeautifulSoup:
    """
    Populate the fields common to both staff and student patron records.

    Args:
        patron: An XML template for a patron record
        patron_record: A patron record as a tuple.
    """
    patron_dict = dict(zip(COMMON_FIELDS, patron_record))
    primary_id = ""
    if patron_dict["KRB_NAME_UPPERCASE"]:
        primary_id = f"{patron_dict['KRB_NAME_UPPERCASE']}@MIT.EDU"
    elif patron_dict["EMAIL_ADDRESS"]:
        primary_id = patron_dict["EMAIL_ADDRESS"]
    patron.primary_id.string = primary_id  # type: ignore
    patron.expiry_date.string = six_months  # type: ignore
    patron.purge_date.string = two_years  # type: ignore

    if patron_dict["EMAIL_ADDRESS"]:
        patron.email_address.string = patron_dict["EMAIL_ADDRESS"]  # type: ignore
    else:
        patron.emails.clear()  # type: ignore

    user_identifiers = patron.find_all("user_identifier")
    for user_identifier in user_identifiers:
        if user_identifier.find("id_type", desc="Additional"):
            mit_id = user_identifier.value
        elif user_identifier.find("id_type", desc="Barcode"):
            library_id = user_identifier.value
    mit_id.string = patron_dict["MIT_ID"] or ""
    if patron_dict["LIBRARY_ID"] and patron_dict["LIBRARY_ID"] != "NONE":
        library_id.string = patron_dict["LIBRARY_ID"] or ""
    else:
        library_id.parent.decompose()
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
        patron = BeautifulSoup(xml_template, features="xml")

        six_months = (date.today() + relativedelta(months=+6)).strftime(
            "%Y-%m-%d"
        ) + "Z"
        two_years = (date.today() + relativedelta(years=+2, months=+6)).strftime(
            "%Y-%m-%d"
        ) + "Z"

        for patron_record in patron_records:
            patron = populate_patron_common_fields(
                patron,
                patron_record,
                six_months,
                two_years,
            )
            if patron_type == "staff":
                pass
            elif patron_type == "student":
                pass
            yield patron
