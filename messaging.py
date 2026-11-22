
"""Say messaging module.

Reserved for the future encrypted messaging implementation.
"""


def send_message(sender_id, recipient_id, encrypted_payload):
    raise NotImplementedError(
        "Messaging will be implemented with E2EE."
    )


def get_conversation(user_id, other_user_id):
    raise NotImplementedError(
        "Conversation retrieval will be implemented later."
    )
