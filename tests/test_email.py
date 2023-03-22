from email.message import EmailMessage

from patronload.email import Email


def test_populate_email_with_all_data():
    email = Email()
    email.populate(
        "from@example.com",
        ["to_1@example.com", "to_2@example.com"],
        "Hello, it's an email!",
        attachments=[
            {
                "content": "Some text content",
                "filename": "attachment.txt",
            }
        ],
        body="I am the message body",
        bcc=["bcc_1@example.com", "bcc_2@example.com"],
        cc=["cc_1@example.com", "cc_2@example.com"],
        reply_to="reply@example.com",
    )
    assert isinstance(email, EmailMessage)
    assert email["From"] == "from@example.com"
    assert email["To"] == "to_1@example.com, to_2@example.com"
    assert email["Subject"] == "Hello, it's an email!"
    assert email["Bcc"] == "bcc_1@example.com, bcc_2@example.com"
    assert email["Cc"] == "cc_1@example.com, cc_2@example.com"
    assert email["Reply-To"] == "reply@example.com"
    assert email.get_content_type() == "multipart/mixed"
    assert email.get_body().get_content() == "I am the message body\n"
    attachment = next(email.iter_attachments())
    assert attachment.get_content() == "Some text content\n"


def test_send_email(mocked_ses):  # pylint: disable=W0613
    email = Email()
    email.populate(
        "from@example.com",
        "to_1@example.com,to_2@example.com",
        "Hello, it's an email!",
        bcc="bcc@example.com",
        cc="cc_1@example.com,cc_2@example.com",
    )
    response = email.send()
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
