from services.phoneburner_svc import add_folders, get_all_contacts_after_update, get_all_phoneburner_folders, add_contact, update_contact, get_all_phoneburner_contacts, update_contact_custom_fields
from services.pipedrive_svc import get_organization, get_person, get_all_pipedrive_organizations, get_all_pipedrive_contacts, get_latest_pipedrive_contacts_since_last_update
from utils.constants import PIPEDRIVE_SOURCE_DETAIL_ID, sync_status, phone_type, status, stake_holder, campaign, score
from data.repository import upsert_organization, get_organization_by_name, upsert_contact, get_contact_by_pd_ref, add_contact_sync_log, create_run_log, get_latest_run_log
from models import Organization, Contact, ContactSyncLog, RunLogs
from utils.constants import PHONEBURNER_CUSTOM_JOB_PD_REF_ID
import pprint
import os

from datetime import datetime, timedelta

ddebug = 1
owner_id = 1167497775
org_id = 66017789


def sync_latest_pipedrive_contacts():
    run_log = get_latest_run_log()
    if run_log:
        last_update = run_log.run_start_time
        contacts_list = get_latest_pipedrive_contacts(last_update)
        for contact in contacts_list:
            sync_to_phoneburner_from_pipedrive(contact["id"])


def add_run_log(run_id, run_mode, run_start_time, run_end_time, run_status):
    run_log = RunLogs(
        run_id=run_id,
        run_mode=run_mode,
        run_start_time=run_start_time,
        run_end_time=run_end_time,
        run_status=run_status
    )
    create_run_log(run_log)


def sync_to_phoneburner_from_pipedrive(pd_ref):
    print(f"[DEBUG] Syncing to phoneburner for pd_ref: {pd_ref}")
    pipedrive_person = get_person(pd_ref)

    db_contact = get_contact_by_pd_ref(pd_ref)

    print(f"[DEBUG] DB Contact: {db_contact}")

    print(f"[DEBUG] Pipedrive Person: {pipedrive_person}")
    if not db_contact:
        contact = Contact(
            first_name=pipedrive_person["first_name"],
            last_name=pipedrive_person["last_name"],
            pd_ref=pipedrive_person["id"],
            source_detail=pipedrive_person[PIPEDRIVE_SOURCE_DETAIL_ID],
            pd_org_id=pipedrive_person["org_id"]["value"],
        )
        upsert_contact(contact)
    if pipedrive_person:
        if pipedrive_person[PIPEDRIVE_SOURCE_DETAIL_ID] == "PPD":
            record = map_person_to_phoneburner(pipedrive_person)

            response = add_contact(record)

            print(f"[DEBUG] Response: {response}")
            print(response["contacts"]["contacts"]["user_id"])
            print(response["contacts"]["contacts"]["import_result"])
            contact_sync_log = ContactSyncLog(
                contact_id=db_contact.id,
                sync_status=response["contacts"]["contacts"]["import_result"],
                sync_type="pipedrive_to_phoneburner",
                phoneburner_id=response["contacts"]["contacts"]["user_id"],
                pipedrive_id=pipedrive_person["id"],
                sync_time=datetime.now()
            )
            print(f"[DEBUG] Contact Sync Log: {contact_sync_log}")
            add_contact_sync_log(contact_sync_log)

            contact = get_contact_by_pd_ref(pd_ref)
            print(f"[DEBUG] Response Status: {response['status']}")
            contact.pb_ref = response["contacts"]["contacts"]["user_id"]
            print(f"[DEBUG] Contact: {contact}")
            upsert_contact(contact)
            return response['status']

    else:
        return "Person not found"


def map_person_to_phoneburner(person):
    record = {}
    additional_phone = []
    custom_fields = []

    record.clear()
    additional_phone.clear()
    custom_fields.clear()

    category_id = check_pb_folders(person["org_name"])

    record["category_id"] = category_id

    # This check confirms status
    match person["e70469ee79a29fdbfb41156db861a30375998171"]:
        case "268" | "241" | "242" | "243" | "251":
            print(
                f"USER_NAME: {person['first_name']} {person['last_name']} with USER_ID: {person['id']} update failed due to status of '{status[person['e70469ee79a29fdbfb41156db861a30375998171']]}'",)
            return None

    # # Check if pd_ref exists in pd_refs_to_skip
    # if person["id"] in pd_refs_to_skip:
    #     print(f"[SKIP] USER_ID: {person['id']}")
    #     return None

    # This check condfirms that PPD is the Source Details
    if person["dafb6c25356831f20d19e81c1cd7a7112d3f5dfd"] in ["PPD", "RiseNow", "TitanX", "Triton"]:
        # print(f"[CREATE] USER_ID: {people[person]["id"]} phoneburner format")
        record["owner_id"] = owner_id
        record["email"] = person["primary_email"]
        record["first_name"] = person["first_name"]
        record["last_name"] = person["last_name"]

        # pprint.pp(people[person],indent=4)
        # print("\n")

        bad_nums = [
            "(403) 231-3900",
            "(403) 205-8300",
            "(832) 636-1009",
        ]

        for num in person["phone"]:
            match num["primary"]:
                case True if (
                    num["value"] != "true"
                    and num["value"] != ""
                    and num["value"] != "N/A"
                    and num["value"] not in bad_nums
                ):
                    # print(f'Primary {num["value"]}')
                    record["phone"] = num["value"]
                    record["phone_type"] = phone_type[num["label"]]
                    record["phone_label"] = num["label"]
                case _ if (
                    num["value"] != "true"
                    and num["value"] != ""
                    and num["value"] != "N/A"
                    and num["value"] not in bad_nums
                ):
                    # print(f'Secondary {num["value"]}')
                    additional_phone.append(
                        {
                            "number": num["value"],
                            "phone_type": phone_type[num["label"]],
                            "phone_label": num["label"],
                        }
                    )

        record["additional_phone"] = additional_phone
        record["city"] = person[
            "f02fa455ab3b42fa7caf5f439f154c44ec0785cc"
        ]
        record["address1"] = person["postal_address"]
        record["state"] = person[
            "e92f3b7d08e6fbb0e7386df5cd23790239ee8f3f"
        ]

        custom_fields.append(
            {
                "custom_field_id": "888920",
                "name": "LinkedIn URL",
                "type": 1,
                "value": person[
                    "795c74fcbe59c8cb0972126a2d758b460addece6"
                ],
            }
        )
        custom_fields.append(
            {
                "custom_field_id": "888710",
                "name": "Company Name",
                "type": 1,
                "value": person["org_name"],
            }
        )
        if person["771702042524dcf97c2d4eb3ba8488e1b3db6978"]:
            print(
                f"[DEBUG] Stakeholder: {person['771702042524dcf97c2d4eb3ba8488e1b3db6978']}")
            custom_fields.append(
                {
                    "custom_field_id": "888928",
                    "name": "Stakeholder Type",
                    "type": 1,
                    "value": stake_holder.get(
                        person[
                            "771702042524dcf97c2d4eb3ba8488e1b3db6978"], f"Unexpected Stakeholder: {person['771702042524dcf97c2d4eb3ba8488e1b3db6978']}",
                    ),
                }
            )
        if person["4a67abb3e361cde03b50511b1171cdabc1ce54a3"]:
            print(
                f"[DEBUG] Campaign: {person['4a67abb3e361cde03b50511b1171cdabc1ce54a3']}")
            print(
                f"[DEBUG] Campaign: {campaign.get(person['4a67abb3e361cde03b50511b1171cdabc1ce54a3'])}")
            custom_fields.append(
                {
                    "custom_field_id": "888929",
                    "name": "Campaign",
                    "type": 1,
                    "value": campaign.get(
                        person["4a67abb3e361cde03b50511b1171cdabc1ce54a3"], "",),
                }
            )

        custom_fields.append(
            {
                "custom_field_id": "888931",
                "name": "Score",
                "type": 7,
                "value": score.get(
                    person["be0137322e663cdca1a5ff7706c73d8e368b839c"], "0",),
            }
        )
        custom_fields.append(
            {
                "custom_field_id": "889001",
                "name": "Job Title",
                "type": 1,
                "value": person["job_title"],
            }
        )
        custom_fields.append(
            {
                "custom_field_id": "889967",
                "name": "pd_ref",
                "type": 7,
                "value": person["id"],
            }
        )

        record["custom_fields"] = custom_fields
        return record
    return None


def sync():
    records = []
    """Sync pipedrive to phoneburner"""

    report_sync = {}
    repeat_check = []
    company_array = {}

    # Get list of pd_refs for contacts updated in the last 24 hours
    pd_refs_to_skip = get_latest_updated_contact_refs()

    response_data = get_organization(0, 500)

    print(f"[Report] Sync Date: {datetime.now()}")
    print(f"[Report] Total Companys: {len(response_data)}")
    report_sync["Sync Date"] = str(datetime.now())
    report_sync["Total Companys"] = len(response_data)

    for org in range(len(response_data)):

        org = org + 18
        print(f"[DEBUG] Org Number - {org}")

        new_record = 0

        # if org == 17:
        #    quit()

        company_id = response_data[org]["id"]
        company_name = response_data[org]["name"]
        company_status = response_data[org]["2705a7de12d92d72d4dae256167264bfc3d63477"]
        report_sync[company_name] = {}
        report_sync[company_name].update({"id": company_id})
        report_sync[company_name].update({"name": company_name})
        report_sync[company_name].update(
            {"status": sync_status[company_status]})
        report_sync[company_name].update(
            {"people": response_data[org]["people_count"]})

        # Check if Company Status == "Loaded"
        # 281 = Loaded
        # 282 = Synced
        if company_status == "281":

            ###################
            # Company Section #
            ###################
            print(f"[Report] Company Name: {company_name}  id:[{company_id}]")
            print(
                f'[Report] Total People: {response_data[org]["people_count"]}')
            print(
                f"[Report] Status: {sync_status[company_status]}  id:[{company_status}]"
            )

            if ddebug == 1:
                pprint.pp(response_data[org], indent=4)

            # Check folders in Phone Burner update with Category_Id
            category_id = check_pb_folders(company_name)

            ###################
            # People Section  #
            ###################
            people = get_people(company_id, 0, 500)

            for person in range(len(people)):
                record = {}
                additional_phone = []
                custom_fields = []

                record.clear()
                additional_phone.clear()
                custom_fields.clear()

                record["category_id"] = category_id

                # This check confirms status
                match people[person]["e70469ee79a29fdbfb41156db861a30375998171"]:
                    case "268" | "241" | "242" | "243" | "251":
                        print(
                            f"USER_NAME: {people[person]['first_name']} {people[person]['last_name']} with USER_ID: {people[person]['id']} update failed due to status of '{status[people[person]['e70469ee79a29fdbfb41156db861a30375998171']]}'",

                        )
                        continue

                # Check if pd_ref exists in pd_refs_to_skip
                if people[person]["id"] in pd_refs_to_skip:
                    print(f"[SKIP] USER_ID: {people[person]['id']}")
                    continue

                # This check condfirms that PPD is the Source Details
                match people[person]["dafb6c25356831f20d19e81c1cd7a7112d3f5dfd"]:
                    case "PPD":
                        new_record = new_record + 1
                        # print(f"[CREATE] USER_ID: {people[person]["id"]} phoneburner format")
                        record["owner_id"] = owner_id
                        record["email"] = people[person]["primary_email"]
                        record["first_name"] = people[person]["first_name"]
                        record["last_name"] = people[person]["last_name"]

                        # pprint.pp(people[person],indent=4)
                        # print("\n")

                        bad_nums = [
                            "(403) 231-3900",
                            "(403) 205-8300",
                            "(832) 636-1009",
                        ]

                        for num in people[person]["phone"]:
                            match num["primary"]:
                                case True if (
                                    num["value"] != "true"
                                    and num["value"] != ""
                                    and num["value"] != "N/A"
                                    and num["value"] not in bad_nums
                                ):
                                    # print(f'Primary {num["value"]}')
                                    record["phone"] = num["value"]
                                    record["phone_type"] = phone_type[num["label"]]
                                    record["phone_label"] = num["label"]
                                case _ if (
                                    num["value"] != "true"
                                    and num["value"] != ""
                                    and num["value"] != "N/A"
                                    and num["value"] not in bad_nums
                                ):
                                    # print(f'Secondary {num["value"]}')
                                    additional_phone.append(
                                        {
                                            "number": num["value"],
                                            "phone_type": phone_type[num["label"]],
                                            "phone_label": num["label"],
                                        }
                                    )

                        record["additional_phone"] = additional_phone
                        record["city"] = people[person][
                            "f02fa455ab3b42fa7caf5f439f154c44ec0785cc"
                        ]
                        record["address1"] = people[person]["postal_address"]
                        record["state"] = people[person][
                            "e92f3b7d08e6fbb0e7386df5cd23790239ee8f3f"
                        ]

                        custom_fields.append(
                            {
                                "custom_field_id": "888920",
                                "name": "LinkedIn URL",
                                "type": 1,
                                "value": people[person][
                                    "795c74fcbe59c8cb0972126a2d758b460addece6"
                                ],
                            }
                        )
                        custom_fields.append(
                            {
                                "custom_field_id": "888710",
                                "name": "Company Name",
                                "type": 1,
                                "value": people[person]["org_name"],
                            }
                        )
                        if people[person]["771702042524dcf97c2d4eb3ba8488e1b3db6978"]:
                            custom_fields.append(
                                {
                                    "custom_field_id": "888928",
                                    "name": "Stakeholder Type",
                                    "type": 1,
                                    "value": stake_holder.get(
                                        people[person][
                                            "771702042524dcf97c2d4eb3ba8488e1b3db6978"], f"Unexpected Stakeholder: {people[person]['771702042524dcf97c2d4eb3ba8488e1b3db6978']}",
                                    ),
                                }
                            )
                        if people[person]["4a67abb3e361cde03b50511b1171cdabc1ce54a3"]:
                            custom_fields.append(
                                {
                                    "custom_field_id": "888929",
                                    "name": "Campaign",
                                    "type": 1,
                                    "value": campaign.get(
                                        people[person]["4a67abb3e361cde03b50511b1171cdabc1ce54a3"], f"Unexpected Campaign: {people[person]['4a67abb3e361cde03b50511b1171cdabc1ce54a3']}",),
                                }
                            )
                        if people[person]["be0137322e663cdca1a5ff7706c73d8e368b839c"]:
                            custom_fields.append(
                                {
                                    "custom_field_id": "888931",
                                    "name": "Score",
                                    "type": 7,
                                    "value": score.get(
                                        people[person]["be0137322e663cdca1a5ff7706c73d8e368b839c"], f"Unexpected Score: {people[person]['be0137322e663cdca1a5ff7706c73d8e368b839c']}",),
                                }
                            )
                        custom_fields.append(
                            {
                                "custom_field_id": "889001",
                                "name": "Job Title",
                                "type": 1,
                                "value": people[person]["job_title"],
                            }
                        )
                        custom_fields.append(
                            {
                                "custom_field_id": "889967",
                                "name": "pd_ref",
                                "type": 7,
                                "value": people[person]["id"],
                            }
                        )

                        record["custom_fields"] = custom_fields

                        print(record)
                        # Add new record

                        # if ddebug == 1:
                        #     pprint.pp(record, indent=4)
                        # #test = api_phoneburner.add_contact(record)
                        # if ddebug == 1:
                        #     print("\n")
                        #     print("RESPONSE")
                        #     pprint.pp(test, indent=4)
                        # if test is None:
                        #     typer.secho(
                        #         f"{person} USER_NAME: {people[person]['first_name']} {people[person]['last_name']} update failed - test is None",
                        #         fg=typer.colors.RED,
                        #     )
                        # elif test["contacts"]["contacts"]["user_id"] in repeat_check:
                        #     typer.secho(
                        #         f"{person} USER_NAME: {people[person]['first_name']} {people[person]['last_name']} with USER_ID: {test['contacts']['contacts']['user_id']} update failed",
                        #         fg=typer.colors.RED,
                        #     )
                        # else:
                        #     repeat_check.append(test["contacts"]["contacts"]["user_id"])
                        #     print(
                        #         f"{person} [API] USER_NAME: {people[person]['first_name']} {people[person]['last_name']} with USER_ID: {people[person]['id']} Added to phoneburner as {test['contacts']['contacts']['user_id']}"
                        #     )

                    case _:
                        pass

        print(
            f"[Report] {new_record} People have been updated in {company_name}\n")
        report_sync[company_name].update(
            {"report": f"{new_record} People have been updated in {company_name}"}
        )

        pprint.pp(report_sync, indent=4)


def sync_pipedrive_organizations():
    print(f"[DEBUG] Syncing Pipedrive Organizations")
    pipedrive_orgs = get_all_pipedrive_organizations()
    print(pipedrive_orgs)
    for pipedrive_org in pipedrive_orgs:
        print(f"[DEBUG] Syncing {pipedrive_org['name']}")
        org = Organization(
            name=pipedrive_org["name"],
            pd_ref=pipedrive_org["id"],
        )

        upsert_organization(org)
        print(org)


def sync_phoneburner_organizations():
    print(f"[DEBUG] Syncing Phoneburner Organizations")
    pb_orgs = get_all_phoneburner_folders()

    for item in pb_orgs["folders"]:
        try:
            if pb_orgs["folders"][item]["folder_name"]:
                print(pb_orgs["folders"][item]["folder_name"])
                org = get_organization_by_name(
                    pb_orgs["folders"][item]["folder_name"])
                if org:
                    org.pb_ref = pb_orgs["folders"][item]["folder_id"]
                    print(f"[DEBUG] Updating {org.name} with {org.pb_ref}")
                    upsert_organization(org)
                else:
                    print(f"[CREATE] Create Folder in phoneburner")
                    company = {}
                    company["name"] = pb_orgs["folders"][item]["folder_name"]
                    company["parent_id"] = org_id
                    # new_pb_folder = add_folders(company)
                    # print(
                    #     f"[CREATED] New folder id: {new_pb_folder['folders']['0']['id']} Company Name: {company_name}")
                    # return new_pb_folder["folders"]["0"]["id"]
        except Exception:
            pass

    # for pb_org in pb_orgs["folders"]:
    #     org = get_organization_by_name(pb_org["folder_name"])
    #     print(org)
    #     if org:
    #         org.pb_ref = pb_org["folder_id"]
    #         upsert_organization(org)
    #     else:
    #         print(f"[CREATE] Create Folder in phoneburner")
    #         company = {}
    #         company["name"] = pb_org["folder_name"]
    #         company["parent_id"] = org_id

    print(pb_orgs)


def sync_pipedrive_contacts():
    pd_orgs = get_all_pipedrive_organizations()
    for pd_org in pd_orgs:
        print(f"[DEBUG] Syncing {pd_org['name']}")
        people = get_all_pipedrive_contacts(pd_org["id"], 0, 500)
        for person in people:
            contact = Contact(
                first_name=person["first_name"],
                last_name=person["last_name"],
                pd_ref=person["id"],
                source_detail=person[PIPEDRIVE_SOURCE_DETAIL_ID],
                pd_org_id=pd_org["id"],
                is_active=True
            )
            print(
                f"[DEBUG] Syncing {person['first_name']} {person['last_name']}")
            upsert_contact(contact)


def sync_phoneburner_contacts():
    contacts = get_all_phoneburner_contacts()
    for contact in contacts:
        print(
            f"[DEBUG] Syncing {contact['first_name']} {contact['last_name']}")

        for custom_field in contact["custom_fields"]:
            if custom_field["custom_field_id"] == PHONEBURNER_CUSTOM_JOB_PD_REF_ID:
                pd_ref = custom_field["value"]
                pipedrive_contact = get_contact_by_pd_ref(pd_ref)
                if pipedrive_contact:
                    pipedrive_contact.pb_ref = contact["user_id"]
                    print(f"[DEBUG] Contact exists in pipedrive")
                    upsert_contact(pipedrive_contact)
                else:
                    print(f"[DEBUG] Contact does not exist in pipedrive")


# Utility Function
###################################################################################
def check_pb_folders(company_name):
    """Two functions use this utility"""

    check_var = False

    # Find Phoneburner Company
    pb_folders = get_all_phoneburner_folders()

    for item in pb_folders["folders"]:
        try:
            if pb_folders["folders"][item]["folder_name"] == company_name:
                check_var = True
                return pb_folders["folders"][item]["folder_id"]

        except Exception:
            pass

    if check_var == False:
        print("[ERROR] No Company Found")
        print(f"[CREATE] Create Folder in phoneburner")
        company = {}
        company["name"] = company_name
        company["parent_id"] = org_id
        new_pb_folder = add_folders(company)
        print(
            f"[CREATED] New folder id: {new_pb_folder['folders']['0']['id']} Company Name: {company_name}")
        return new_pb_folder["folders"]["0"]["id"]


def get_latest_updated_contact_refs():
    last_update = (datetime.today() - timedelta(days=1)
                   ).strftime("%Y-%m-%d %H:%M:%S")
    contacts_list = get_all_contacts_after_update(last_update)

    # Compile an array of `pd_ref` values
    pd_ref_values = [
        int(field["value"])
        for contact in contacts_list
        if "custom_fields" in contact
        for field in contact["custom_fields"]
        if field.get("name") == "pd_ref"
    ]
    return pd_ref_values


def get_latest_pipedrive_contacts(last_update):
    contacts_list = get_latest_pipedrive_contacts_since_last_update(
        last_update)
    return contacts_list


sync_latest_pipedrive_contacts()
