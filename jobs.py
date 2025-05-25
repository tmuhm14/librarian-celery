# from services.phoneburner_svc import get_all_phoneburner_contacts, update_contact_custom_fields, get_custom_field
# import json
# import os
# from dotenv import load_dotenv
# from utils import constants

# load_dotenv()


# def pull_phoneburner_contacts():
#     contacts = get_all_phoneburner_contacts()
#     # save to file
#     with open("phoneburner_contacts.json", "w") as f:
#         json.dump(contacts, f)
#     print(contacts)

# # read from file


# def read_phoneburner_contacts():
#     with open("phoneburner_contacts.json", "r") as f:
#         contacts = json.load(f)
#         for contact in contacts:
#             # print(contact["custom_fields"])
#             for field in contact["custom_fields"]:
#                 print(field)
#                 if field["custom_field_id"] == constants.PHONEBURNER_CUSTOM_SCORE_ID:
#                     print(field["value"])


# if __name__ == "__main__":
#     # pull_phoneburner_contacts()
#     # read_phoneburner_contacts()
#     update_contact_custom_fields(
#         1203158988, constants.PHONEBURNER_CUSTOM_SCORE_NUM_ID, 5)
#     # update_custom_field(
#     #     1203158988, constants.PHONEBURNER_CUSTOM_SCORE_NUM_ID, 5)
#     # get_custom_field(1203158988, constants.PHONEBURNER_CUSTOM_SCORE_NUM_ID)
