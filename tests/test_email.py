from email.message import EmailMessage
from http import HTTPStatus

from patronload.email import Email


def test_populate_email_with_all_data():
    email = Email()
    email.populate(
        from_address="from@example.com",
        to_addresses=["to_1@example.com", "to_2@example.com"],
        subject="Hello, it's an email!",
        body="I am the message body",
    )
    assert isinstance(email, EmailMessage)
    assert email["From"] == "from@example.com"
    assert email["To"] == "to_1@example.com, to_2@example.com"
    assert email["Subject"] == "Hello, it's an email!"
    assert email.get_content_type() == "text/plain"
    assert email.get_body().get_content() == "I am the message body\n"


def test_send_email(mocked_ses):
    email = Email()
    email.populate(
        from_address="from@example.com",
        to_addresses="to_1@example.com,to_2@example.com",
        subject="Hello, it's an email!",
    )
    response = email.send()
    assert response["ResponseMetadata"]["HTTPStatusCode"] == HTTPStatus.OK
