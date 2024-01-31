import json
import os
import shutil

import requests


def get_api_data(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def setup_topics_folder():
    """
    Prepare the topics folder for the training material and the eosc jsons
    """
    if os.path.exists("./old_topics"):
        shutil.rmtree("./old_topics")
    if os.path.exists("./topics"):
        shutil.move("./topics", "./old_topics")
    os.mkdir("./topics")
    if os.path.exists("./eosc_jsons"):
        shutil.rmtree("./eosc_jsons")
    os.mkdir("./eosc_jsons")


def process_topics():
    """
    Fetch the training material for each topic and save it as a json file in the topics folder
    """
    topics_url = "https://training.galaxyproject.org/training-material/api/topics.json"
    topics = get_api_data(topics_url)
    for topic in topics:
        topic_folder = f"./topics/{topic}"
        os.mkdir(topic_folder)
        topic_url = f"https://training.galaxyproject.org/training-material/api/topics/{topic}.json"
        topic_training_material = get_api_data(topic_url)["materials"]
        for training in topic_training_material:
            id = f"{training['topic_name']}_{training['tutorial_name']}"
            training_json = f"{topic_folder}/{id}.json"
            with open(training_json, "w") as f:
                json.dump(training, f, sort_keys=True, indent=4)


def translate_level(level):
    """
    Translate the level of the training material to the eosc format
    """
    level_mapping = {
        "Introductory": "tr_expertise_level-beginner",
        "Any": "tr_expertise_level-all",
        "Intermediate": "tr_expertise_level-intermediate",
        "Advanced": "tr_expertise_level-advanced",
    }
    return (
        level_mapping.get(level, "tr_expertise_level-advanced")
        or "tr_expertise_level-all"
    )


def training_to_eosc_json(training_json):
    """
    Convert the training json to a eosc json
    """
    with open(training_json) as f:
        training = json.load(f)

    # --- Basic Information ---
    id = training.get("id")
    title = training.get("tutorial_name")
    provider_id = "uni-freiburg"
    # resource_providers = ...
    contributors = training.get("contributors")
    authors = [contributor.get("name") for contributor in contributors]
    webpage = "https://training.galaxyproject.org/training-material" + training.get(
        "url"
    )
    # url_type = ...
    # eoscRelatedServices = ...
    # alternative_identifiers = ...
    # description = ...
    # keywords = ...
    # TODO - Think about how to set license dynamically
    license = "https://spdx.org/licenses/CC-BY-4.0"
    # TODO - Are the access rights always the same?
    access_rights = "tr_access_right-open_access"
    # TODO - Think about how to set the version data dynamically
    version_date = "2024-01-01"

    # --- Learning Information ---
    targetGroups = ["target_user-researchers", "target_user-students"]
    learningOutcomes = [objective for objective in training.get("objectives")]
    # learningResourceTypes = ...
    expertiseLevel = translate_level(training.get("level"))
    # contentResourceTypes = ...
    # qualifications = ...
    duration = training.get("time_estimation")

    # --- Geographical and Language Availability Information ---
    languages = ["en"]
    geographicalAvailabilities = ["WW"]

    # --- Classification Information ---
    scientificDomains = [
        {
            "scientificDomain": "scientific_domain-generic",
            "scientificSubdomain": "scientific_subdomain-generic-generic",
        }
    ]

    # --- Contact Information ---
    main_contributor = contributors[0]
    main_name = main_contributor.get("name").split(" ")
    main_email = main_contributor.get("email")
    contact = {
        "firstName": main_name[0],
        "lastName": main_name[-1],
        "email": main_email,
        # "phone": "string",
        # "position": "string",
        # "organisation": "string"
    }
    # catalogueId = ...

    data = {
        "id": id,
        "title": title,
        "resourceOrganisation": provider_id,
        # "resourceProviders": [
        #     "string"
        # ],
        "authors": authors,
        "url": webpage,
        # "urlType": "string",
        # "eoscRelatedServices": ["string"],
        # "alternativeIdentifiers": [
        #     {
        #     "type": "string",
        #     "value": "string"
        #     }
        # ],
        # "description": description, # recommended
        # "keywords": ["string"], # recommended
        "license": license,
        "accessRights": access_rights,
        "versionDate": version_date,
        "targetGroups": targetGroups,
        # "learningResourceTypes": ["string"], # recommended
        "learningOutcomes": learningOutcomes,
        "expertiseLevel": expertiseLevel,
        # "contentResourceTypes": ["string"], # recommended
        # "qualifications": ["string"], # recommended
        "duration": duration,  # recommended
        "languages": languages,
        "geographicalAvailabilities": geographicalAvailabilities,
        "scientificDomains": scientificDomains,
        "contact": contact,
        # "catalogueId": "string"
    }
    return data
    # with open(f"./eosc_jsons/{id}.json", "w") as f:
    #     json.dump(data, f, sort_keys=True, indent=4)
    # return None


# def convert_training_to_eosc_json():
#     training_jsons = [
#         f"./topics/{topic}/{training}"
#         for topic in os.listdir("./topics")
#         for training in os.listdir(f"./topics/{topic}")
#     ]
#     # convert the training jsons to eosc jsons
#     eosc_jsons = [training_to_eosc_json(training_json) for training_json in training_jsons]
#     # first_eosc_json = training_to_eosc_json(training_jsons[0])
#     # write the eosc jsons to a file in separate folder
#     if os.path.exists("./eosc_jsons"):
#         shutil.rmtree("./eosc_jsons")
#     os.mkdir("./eosc_jsons")
#     for eosc_json in eosc_jsons:
#         id = eosc_json.get("id")
#         with open(f"./eosc_jsons/{id}.json", "w") as f:
#             json.dump(eosc_json, f, sort_keys=True, indent=4)

if __name__ == "__main__":
    # setup_topics_folder()
    # process_topics()
    # get the training jsons
    training_jsons = [
        f"./topics/{topic}/{training}"
        for topic in os.listdir("./topics")
        for training in os.listdir(f"./topics/{topic}")
    ]
    # convert the training jsons to eosc jsons
    # eosc_jsons = [
    #     training_to_eosc_json(training_json) for training_json in training_jsons
    # ]
    first_eosc_json = training_to_eosc_json(training_jsons[0])
    with open("eosc_training.json", "w") as f:
        json.dump(first_eosc_json, f, sort_keys=True, indent=4)