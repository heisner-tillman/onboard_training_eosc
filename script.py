import json
import os
import shutil

import requests


def get_api_data(api_url):
    """
    Get the data from the api and return it as a json
    return: the data from the api as a json or the related error message
    """
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def setup_topics_folder():
    """
    Prepare the topics folder for the training material and the eosc jsons
    return: None
    """
    if os.path.exists("./old_topics"):
        shutil.rmtree("./old_topics")
    if os.path.exists("./topics"):
        shutil.move("./topics", "./old_topics")
    os.mkdir("./topics")

    if os.path.exists("./old_upload_failures"):
        shutil.rmtree("./old_upload_failures")
    if os.path.exists("./upload_failures"):
        shutil.move("./upload_failures", "./old_upload_failures")
    os.mkdir("./upload_failures")
    os.mkdir("./upload_failures/new_trainings")
    os.mkdir("./upload_failures/updated_trainings")

    if os.path.exists("./validated_eosc_jsons"):
        shutil.rmtree("./validated_eosc_jsons")
    os.mkdir("./validated_eosc_jsons")
    os.mkdir("./validated_eosc_jsons/updated_trainings")
    os.mkdir("./validated_eosc_jsons/new_trainings")


def fetch_trainings():
    """
    Fetch the training material for each topic and save it as a json file in the topics folder
    return: None
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


def compare_training_material():
    """
    Compare the old and new training material and return the new and updated training material
    return: a dict containing the new and updated training material
    """
    new_trainings = []
    updated_trainings = []
    for topic in os.listdir("./topics"):
        for training in os.listdir(f"./topics/{topic}"):
            # if the training is in the old topics, compare the trainings
            if os.path.exists(f"./old_topics/{topic}/{training}") and os.path.isfile(
                f"./old_topics/{topic}/{training}"
            ):
                # compare the trainings and if there is a change, add it to the updated_trainings
                with open(f"./topics/{topic}/{training}") as f:
                    new_training = json.load(f)
                with open(f"./old_topics/{topic}/{training}") as f:
                    old_training = json.load(f)
                if new_training != old_training:
                    updated_trainings.append(f"./topics/{topic}/{training}")
            # if the training is not in the old topics, add it to the new_trainings
            else:
                new_trainings.append(f"./topics/{topic}/{training}")

            # if the training failed the validation in the previous run
            # add it to the corresponding training list
            if os.path.exists(
                f"./old_upload_failures/new_trainings/{training}"
            ) and os.path.isfile(f"./old_upload_failures/new_trainings/{training}"):
                new_trainings.append(f"./topics/{topic}/{training}")
            if os.path.exists(
                f"./old_upload_failures/updated_trainings/{training}"
            ) and os.path.isfile(f"./old_upload_failures/updated_trainings/{training}"):
                updated_trainings.append(f"./topics/{topic}/{training}")

    return {"new_trainings": new_trainings, "updated_trainings": updated_trainings}


def translate_level(level: str):
    """
    Translate the level of the training material to the eosc format
    return: the expertise level of the training material in the eosc format
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


def training_to_eosc_json(training_json: str):
    """
    Convert the training json to a format that the eosc training material accepts
    See https://wiki.eoscfuture.eu/display/PUBLIC/F.+EOSC+Training+Resource+Profile for reference
    return: a tuple with the converted json/error message and the training name
    """
    with open(training_json) as f:
        training = json.load(f)
    try:
        mandatory_fields = []

        # --- Basic Information ---
        id = training.get("id")
        title = training.get("tutorial_name")
        provider_id = "uni-freiburg"
        # resource_providers = ...
        contributors = training.get("contributors")
        authors = []
        if training.get("contributions") and "authorship" in training.get(
            "contributions"
        ):
            author_ids = training.get("contributions").get("authorship")
            for contributor in contributors:
                if contributor.get("id") in author_ids:
                    authors.append(contributor.get("name"))
        else:
            authors = [contributor.get("name") for contributor in contributors]
        authors = list(dict.fromkeys(authors))
        webpage = "https://training.galaxyproject.org/training-material" + training.get(
            "url"
        )
        # url_type = ...
        # eoscRelatedServices = ...
        # alternative_identifiers = ...

        # --- Detailed & access Information ---
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
        objectives = training.get("objectives")
        if objectives:
            learningOutcomes = [objective for objective in objectives]
        else:
            learningOutcomes = ["No learning outcomes available"]
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
        # TODO get the email of the first person of the board of the topic and replace placeholder email
        main_email = main_contributor.get("email") or "place_holder@uni-freiburg.com"
        contact = {
            "firstName": main_name[0],
            "lastName": main_name[-1],
            "email": main_email,
            # "phone": "string",
            # "position": "string",
            # "organisation": "string"
        }
        # catalogueId = ...

        # TODO - populate the optional fields above

        # Append variables to mandatory_fields
        mandatory_fields.append(("id", id))
        mandatory_fields.append(("title", title))
        mandatory_fields.append(("resourceOrganisation", provider_id))
        mandatory_fields.append(("authors", authors))
        mandatory_fields.append(("url", webpage))
        mandatory_fields.append(("license", license))
        mandatory_fields.append(("accessRights", access_rights))
        mandatory_fields.append(("versionDate", version_date))
        mandatory_fields.append(("targetGroups", targetGroups))
        mandatory_fields.append(("learningOutcomes", learningOutcomes))
        mandatory_fields.append(("expertiseLevel", expertiseLevel))
        mandatory_fields.append(("languages", languages))
        mandatory_fields.append(
            ("geographicalAvailabilities", geographicalAvailabilities)
        )
        mandatory_fields.append(("scientificDomains", scientificDomains))
        mandatory_fields.append(("contact", contact))

        # Check if all mandatory fields are set
        for field in mandatory_fields:
            if not field[1]:
                return (
                    f"For {training_json} the mandatory field {field[0]} is not set",
                    training_json,
                )
            if field[1] == []:
                return (
                    f"For {training_json} the mandatory field {field[0]} is empty",
                    training_json,
                )
            if type(field[1]) == dict:
                for key, value in field[1].items():
                    if not value:
                        return (
                            f"For {training_json} the mandatory field {key} is not set",
                            training_json,
                        )

    # catch all exceptions
    except Exception as e:
        return (f"For {training_json} there was an error: {e}", training_json)

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
    return (data, training_json)


def validate_eosc_json(eosc_json):
    """
    Validate the eosc json by checking the payload for errors that arose during the conversion.
    If there are no errors, send the json to the eosc training material api for validation.
    return: a tuple with the validation response and the training name
    """
    payload = eosc_json[0]
    training = eosc_json[1]
    if type(payload) != dict:
        return (f"Json conversion error: \n{payload}", training)

    url = "https://api.eosc-portal.eu/trainingResource/validate"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        return f"API error: \n{response.text}", training, payload
    return response.json(), training, payload


def process_validated_trainings(validated_new_trainings, validated_updated_trainings):
    """
    Divide the validated trainings into valid and invalid responses and move/copy them to the corresponding folders
    return: None
    """
    for training in validated_new_trainings:
        if str(training[0]) == "True":
            # write the converted training to a file in validated_eosc_jsons/new_trainings
            training_name = training[1].split("/")[-1]
            with open(
                f"./validated_eosc_jsons/new_trainings/{training_name}", "w"
            ) as f:
                json.dump(training[2], f, sort_keys=True, indent=4)
        else:
            # copy the failed training to upload_failures/new_trainings
            # and write the error message to a file
            shutil.copy(training[1], "./upload_failures/new_trainings")
            with open("./upload_failures.txt", "a") as f:
                f.write(f"{training}\n")

    for training in validated_updated_trainings:
        if str(training[0]) == "True":
            # write the converted training to a file in validated_eosc_jsons/updated_trainings
            training_name = training[1].split("/")[-1]
            with open(
                f"./validated_eosc_jsons/updated_trainings/{training_name}", "w"
            ) as f:
                json.dump(training[2], f, sort_keys=True, indent=4)
        else:
            # copy the failed training to upload_failures/updated_trainings
            # and write the error message to a file
            shutil.copy(training[1], "./upload_failures/updated_trainings")
            with open("./upload_failures.txt", "a") as f:
                f.write(f"{training}\n")


def upload_training_files(url, headers, authentifier):
    """
    Upload the validated training files to the eosc training material api
    return: a dict containing the number of successful/failed creations/updates and a list of failure messages
    """
    # TODO - handle the responses - failures
    successful_creations = 0
    failed_creations = 0
    successful_updates = 0
    failed_updates = 0
    create_responses_failures = []
    update_responses_failures = []
    for training in os.listdir("./validated_eosc_jsons/new_trainings"):
        with open(f"./validated_eosc_jsons/{training}") as f:
            response = requests.post(url, headers=headers, auth=authentifier, json=f)
            if response.status_code != 200:
                # append the error message to the responses
                create_responses_failures.append(
                    f"An error occurred: {response.text}", training
                )
                failed_creations += 1
            else:
                successful_creations += 1
    for training in os.listdir("./validated_eosc_jsons/updated_trainings"):
        with open(f"./validated_eosc_jsons/{training}") as f:
            response = requests.put(url, headers=headers, auth=authentifier, json=f)
            if response.status_code != 200:
                # append the error message to the responses
                update_responses_failures.append(
                    f"An error occurred: {response.text}", training
                )
                failed_updates += 1
            else:
                successful_updates += 1
    response = {
        "successful_creations": successful_creations,
        "failed_creations": failed_creations,
        "create_responses_failures": create_responses_failures,
        "successful_updates": successful_updates,
        "failed_updates": failed_updates,
        "update_responses_failures": update_responses_failures,
    }
    return response


if __name__ == "__main__":
    # get the current training material from the galaxy training material api
    setup_topics_folder()
    fetch_trainings()
    # check if there are new or updated trainings and if so convert them to eosc jsons
    training_jsons = compare_training_material()
    new_training_eosc_jsons = [
        training_to_eosc_json(training_json)
        for training_json in training_jsons["new_trainings"]
    ]
    update_training_eosc_jsons = [
        training_to_eosc_json(training_json)
        for training_json in training_jsons["updated_trainings"]
    ]
    # validate the converted jsons
    validated_new_trainings = [
        validate_eosc_json(training) for training in new_training_eosc_jsons
    ]
    validated_updated_trainings = [
        validate_eosc_json(training) for training in update_training_eosc_jsons
    ]
    # process the validated trainings
    process_validated_trainings(validated_new_trainings, validated_updated_trainings)

    # TODO - send the valid eosc jsons to the eosc training material api
    # headers = {"Content-Type": "application/json"}
    # authentifier = ("", "")
    # upload_response = upload_training_files(url, headers, authentifier)
