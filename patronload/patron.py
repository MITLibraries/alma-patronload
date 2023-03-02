import logging
import re
from datetime import date
from typing import Any, Generator

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


def create_patron_dicts(
    fields: list[str], patron_records: list[tuple]
) -> Generator[dict, None, None]:
    """
    Create dicts of patron data from a list of patron records.

    Patron records are retrieved as tuples from the Data Warehouse and
    the dicts are returned via a generator.

    Args:
        fields: The fields that serve as keys in the dict.
        patron_records: A list of patron record tuples.
    """
    for patron_record in patron_records:
        patron_dict = {}
        for field in fields:
            patron_dict[field] = patron_record[fields.index(field)]
        yield patron_dict


def format_phone_number(phone_number: str) -> str:
    """
    Format a string of 10 numbers as a phone number with dashes.

    Args:
        phone_number: A string that may contain a phone number.
    """
    return re.sub(r"(\d{3})(\d{3})(\d{4})", r"\1-\2-\3", phone_number)


def populate_patron_common_fields(
    patron: BeautifulSoup, patron_dict: dict[str, Any]
) -> BeautifulSoup:
    """
    Populate the fields common to both staff and student patron records.

    Args:
        patron: An XML template for a patron record
        patron_dict: A dict of patron data used to populate an XML template.
    """
    six_months = date.today() + relativedelta(months=+6)
    two_years = six_months + relativedelta(years=+2)

    patron.find_all("primary_id")[0].string = (
        f"{patron_dict['KRB_NAME_UPPERCASE']}@MIT.EDU"
        if patron_dict["KRB_NAME_UPPERCASE"]
        else patron_dict["EMAIL_ADDRESS"]
    )
    patron.find_all("expiry_date")[0].string = six_months.strftime("%Y-%m-%d") + "Z"
    patron.find_all("purge_date")[0].string = two_years.strftime("%Y-%m-%d") + "Z"

    if patron_dict["EMAIL_ADDRESS"]:
        patron.find_all("email_address")[0].string = patron_dict["EMAIL_ADDRESS"]

    user_identifiers = patron.find_all("user_identifier")
    for user_identifier in user_identifiers:
        if user_identifier.find("id_type", desc="Additional"):
            mit_id = user_identifier.find_all("value")[0]
        elif user_identifier.find("id_type", desc="Barcode"):
            library_id = user_identifier.find_all("value")[0]
    mit_id.string = patron_dict["MIT_ID"] or ""
    if patron_dict["LIBRARY_ID"] and patron_dict["LIBRARY_ID"] != "NONE":
        library_id.string = patron_dict["LIBRARY_ID"] or ""
    return patron


def patron_xml_records_from_dicts(
    patron_type: str, patron_dicts: list
) -> Generator[BeautifulSoup, None, None]:
    """
    Create patron XML records from patron dicts.

    Args:
        patron_type: The type of patron record being processed, staff or student.
        patron_dicts: A list of dicts of patron data used to populate XML templates.
    """
    with open(
        f"config/{patron_type}_template.xml", "r", encoding="utf8"
    ) as xml_template:
        patron = BeautifulSoup(xml_template, features="xml")
        for patron_dict in patron_dicts:
            patron = populate_patron_common_fields(patron, patron_dict)
            if patron_type == "staff":
                pass
            elif patron_type == "student":
                pass
            yield patron
