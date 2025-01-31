from email.message import EmailMessage  # noqa: A005
from email.policy import EmailPolicy, default

import boto3


class Email(EmailMessage):
    """Email subclasses EmailMessage with added functionality to populate and send."""

    def __init__(
        self,
        policy: EmailPolicy = default,  # type: ignore[assignment]
    ) -> None:
        """Initialize Email instance."""
        super().__init__(policy)

    def populate(
        self,
        from_address: str,
        to_addresses: str,
        subject: str,
        body: str | None = None,
    ) -> None:
        """Populate Email message with addresses and subject.

        Optionally add body.

        to_addresses, can take multiple email addresses as a
        single string of comma-separated values

        Attachments parameter should be structured as follows and must include all
        fields for each attachment:
        [
            {
                "content": "Contents of attachment as it would be written to a file-like
                    object",
                "filename": "File name to use for attachment, e.g. 'a_file.xml'"
            },
            {...repeat above for all attachments...}
        ]
        """
        self["From"] = from_address
        self["To"] = to_addresses
        self["Subject"] = subject
        if body:
            self.set_content(body)

    def send(self) -> dict[str, str]:
        """Send email.

        Currently uses SES but could easily be switched out for another method if
        needed.
        """
        ses = boto3.client("ses", region_name="us-east-1")
        destinations = self["To"].split(",")
        return ses.send_raw_email(
            Source=self["From"],
            Destinations=destinations,
            RawMessage={
                "Data": self.as_bytes(),
            },
        )
