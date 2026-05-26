# TVS_DND/reply_generator.py

def generate_reply(inserted_count, existing_count):
    """
    Generates final DND processing reply dynamically.
    """

    # Case 1 - All records already exist
    if inserted_count == 0 and existing_count == 0:

        message = f"""
Hi Team,

Thank you for contacting Karix Provisioning.

As requested, the mobile numbers provided in the attached file have been verified for the DND activation under the voice service account: tvs_voicepr.

No new records were added or updated, as all numbers are already present in the blacklist.

Please review and let us know if you have any concerns.

Thanks & Regards,
Karix Provisioning Team
📞 +91 7760686668 / +91 7207935595
"""

    # Case 2 - New records inserted
    else:

        message = f"""
Hi Team,

Thank you for contacting Karix Provisioning.

As requested, the mobile numbers provided in the attached file have been processed for the DND activation under the voice service account: tvs_voicepr.

{inserted_count} number(s) have been successfully added to the DND list.

{existing_count} number(s) were already present in the blacklist.

Please review and let us know if you have any concerns.

Thanks & Regards,
Karix Provisioning Team
📞 +91 7760686668 / +91 7207935595
"""

    return message.strip()