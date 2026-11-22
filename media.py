
"""Say media module.

Future support:
- Images
- Videos
- Voice messages
- Audio attachments

Media must be encrypted on the sender's device
before upload in the production E2EE implementation.
"""


def prepare_media(file_path):
    raise NotImplementedError(
        "Secure media handling will be implemented later."
    )
