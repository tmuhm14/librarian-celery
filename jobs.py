# from services.phoneburner_svc import get_all_phoneburner_contacts, update_custom_field, get_custom_field
# import json
# import os
# from dotenv import load_dotenv
# from utils import constants

# load_dotenv()


# def pull_phoneburner_contacts():
#     contacts = get_all_phoneburner_contacts()
#     # save to file
#     # with open("phoneburner_contacts.json", "w") as f:
#     #     json.dump(contacts, f)
#     # print(contacts)
#     return contacts

# # read from file


# def read_phoneburner_contacts(contacts):
#     run_log = []

#     for contact in contacts:
#         # print(contact["custom_fields"])
#         found = False
#         pd_ref = None
#         pd_ref_found = False
#         custom_score = 0
#         for field in contact["custom_fields"]:
#             if field["custom_field_id"] == constants.PHONEBURNER_CUSTOM_SCORE_ID:
#                 print(field["value"])
#                 custom_score = field["value"]
#                 found = True
#             if field["custom_field_id"] == constants.PHONEBURNER_CUSTOM_JOB_PD_REF_ID:
#                 pd_ref = field["value"]
#                 pd_ref_found = True

#         if found:
#             print('--------------------------------')
#             print('found')
#             print(custom_score)
#             print(pd_ref)
#             print(contact["user_id"])
#             print('--------------------------------')
#             run_log.append(
#                 f'{contact["user_id"]},{custom_score},{pd_ref}, Found')

#             # run_log.append({
#             #     "user_id": contact["user_id"],
#             #     "custom_score": custom_score
#             # })
#             # update_custom_field(
#             #     contact["user_id"], constants.PHONEBURNER_CUSTOM_SCORE_NUM_ID, custom_score)
#         else:
#             print('--------------------------------')
#             print('not found')
#             print(contact["user_id"])
#             print(pd_ref)
#             print('--------------------------------')
#             run_log.append(f'{contact["user_id"]},0,{pd_ref}, Not Found')
#             # run_log.append({
#             #     "user_id": contact["user_id"],
#             #     "custom_score": 0
#             # })
#             if pd_ref_found:
#                 update_custom_field(
#                     contact["user_id"], constants.PHONEBURNER_CUSTOM_SCORE_ID, 0)
#     with open("run_log.csv", "w") as f:
#         f.write('\n'.join(run_log))


# if __name__ == "__main__":
#     contacts = pull_phoneburner_contacts()
#     read_phoneburner_contacts(contacts)
#     # get_custom_field(1203158988, constants.PHONEBURNER_CUSTOM_SCORE_ID)
#     # update_custom_field(
#     #     1203158988, constants.PHONEBURNER_CUSTOM_SCORE_ID, 0)
#     # get_custom_field(1203158988, constants.PHONEBURNER_CUSTOM_SCORE_ID)
