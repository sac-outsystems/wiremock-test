import json
import os
import pathlib

from invoke import task

from no_ssl_verification import do_not_verify
from wiremock_service import WireMockService


def _load_static_mappings(wiremock: WireMockService):

    mappings_path = os.path.dirname(os.path.realpath(__file__))
    mapping_files = pathlib.Path(mappings_path + "/defaults/mappings").glob("*.json")

    print("Loading mappings...")

    for file in mapping_files:
        print(f"Loading mapping {file} ...")

        with open(file) as mf:
            file_content = json.load(mf)
            mappings = file_content["mappings"]
            for mapping in mappings:
                wiremock.post_mapping(mapping)

    print("Loading responses...")

    files = pathlib.Path(mappings_path + "/defaults/responses").glob("*")

    for file in files:
        print(f"Uploading file {file}")

        with open(file) as mf:
            wiremock.upload_file(file_name=file.name, file_content=mf.read())


@task
def setup_static_mappings(context):

    with do_not_verify():
        wiremock = WireMockService()
        wiremock.delete_all_mappings()

        _load_static_mappings(wiremock)