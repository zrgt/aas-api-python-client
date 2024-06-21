from aas_api_python_client import ApiClient, Configuration, AssetAdministrationShellRepositoryAPIApi
from aas_api_python_client.util import string_to_base64url
from aas_api_python_client.rest import ApiException

from basyx.aas.examples.data.example_aas import *
from basyx.aas.adapter.json import AASToJsonEncoder, StrippedAASToJsonEncoder, StrictStrippedAASFromJsonDecoder
from basyx.aas import model

import json
import unittest
import tempfile
import os


class AASClientTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        configuration = Configuration()
        configuration.host = "http://localhost:8080/api/v3.0"

        cls.api_client = ApiClient(configuration=configuration)
        cls.aasRepoClient = AssetAdministrationShellRepositoryAPIApi(api_client=cls.api_client)

        cls.example_aas = create_example_asset_administration_shell()
        cls.example_submodel = create_example_submodel()
        cls.example_submodel_element = list(cls.example_submodel.submodel_element)[-1]

        cls.example_aas_parsed = cls._parse_object(object=cls.example_aas, encoder=AASToJsonEncoder)

        cls.example_submodel_parsed = cls._parse_object(object=cls.example_submodel, encoder=AASToJsonEncoder)

        cls.example_submodel_metadata = cls._parse_object(object=cls.example_submodel, encoder=StrippedAASToJsonEncoder,
                                                          decoder=StrictStrippedAASFromJsonDecoder)

        cls.example_submodel_element_parsed = cls._parse_object(object=cls.example_submodel_element, encoder=AASToJsonEncoder)

        cls.CHECKER = AASDataChecker(raise_immediately=True)


    @staticmethod
    def _parse_object(object, encoder, decoder=None):
        return json.loads(json.dumps(object, cls=encoder, separators=(",", ":")), cls=decoder)

    def _assert_api_exception(self, function, expected_status, expected_message=None):
        with self.assertRaises(ApiException) as cm:
            function()
        exception = cm.exception
        self.assertEqual(expected_status, exception.status)
        if expected_message:
            response_body = json.loads(exception.body)
            error_message = response_body['messages'][0]['text']
            self.assertEqual(expected_message, error_message)

    def test_cursor_and_limit(self):
        retrieved_aashels = self.aasRepoClient.get_all_asset_administration_shells(cursor=1, limit=1)
        aas_list = retrieved_aashels.result
        self.assertEqual(0, len(aas_list))

    def test_cursor_and_limit_errors(self):
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_all_asset_administration_shells(cursor=-1, limit="a"), 400,
            "Cursor and limit must be positive integers!")

    def test_get_all_aas_single(self):
        retrieved_aashels = self.aasRepoClient.get_all_asset_administration_shells(
            id_short="TestAssetAdministrationShell")
        aas_list = retrieved_aashels.result
        self.CHECKER.check_asset_administration_shell_equal(aas_list[0], self.example_aas)
        self.assertEqual(1, len(aas_list))

    # TODO: fix splitting of asset_id
    def test_get_all_aas_assetid_filtering(self):
        asset_id = ("ew0KCQkJCQkJInNlbWFudGljSWQiOiB7DQoJCQkJCQkJInR5cGUiOiAiRXh0ZXJuYWxSZWZlcmVuY2UiLA0"
                    "KCQkJCQkJCSJrZXlzIjogWw0KCQkJCQkJCQl7DQoJCQkJCQkJCQkidHlwZSI6ICJHbG9iYWxSZWZlcmVuY2"
                    "UiLA0KCQkJCQkJCQkJInZhbHVlIjogImh0dHA6Ly9hY3BsdC5vcmcvU3BlY2lmaWNBc3NldElkLyINCgkJC"
                    "QkJCQkJfQ0KCQkJCQkJCV0NCgkJCQkJCX0sDQoJCQkJCQkibmFtZSI6ICJUZXN0S2V5IiwNCgkJCQkJCSJ2"
                    "YWx1ZSI6ICJUZXN0VmFsdWUiLA0KCQkJCQkJImV4dGVybmFsU3ViamVjdElkIjogew0KCQkJCQkJCSJ0eXB"
                    "lIjogIkV4dGVybmFsUmVmZXJlbmNlIiwNCgkJCQkJCQkia2V5cyI6IFsNCgkJCQkJCQkJew0KCQkJCQkJCQ"
                    "kJInR5cGUiOiAiR2xvYmFsUmVmZXJlbmNlIiwNCgkJCQkJCQkJCSJ2YWx1ZSI6ICJodHRwOi8vYWNwbHQub"
                    "3JnL1NwZWNpZmljQXNzZXRJZC8iDQoJCQkJCQkJCX0NCgkJCQkJCQldDQoJCQkJCQl9DQoJCQkJCX0")
        retrieved_aashels = self.aasRepoClient.get_all_asset_administration_shells(
            asset_ids=asset_id)  # splits up asset_id, filtering does not work
        aas_list = retrieved_aashels.result
        self.CHECKER.check_asset_administration_shell_equal(aas_list[0], self.example_aas)
        self.assertEqual(1, len(aas_list))

    # TODO: fix splitting of asset_id
    def test_get_all_aas_single_errors(self):
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_all_asset_administration_shells(asset_ids="1"), 400,
            "Encoded data 1 is invalid base64url!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_all_asset_administration_shells(
                asset_ids="ew0KCQkJCQkJInNlbWFudGljSWQiOiB7DQoJCQkJCQkJInR5"), 422,
            # should be 422 isn't because filtering is not working
        )

    # TODO: implement this once the deserialization problem of the model.Modelreference objects is fixed
    def test_get_all_aas_references_single(self):
        aas_reference = model.ModelReference.from_referable(self.example_aas)
        retrieved_aashels_references = self.aasRepoClient.get_all_asset_administration_shells_reference()
        aas_list_references = retrieved_aashels_references.result  # for some reason this is not a model.ModelReference
        # object, deserialization is not working
        self.CHECKER._check_reference_equal(aas_list_references[0], aas_reference)

    # TODO: implement this once the deserialization problem of the model.Modelreference objects is fixed
    def test_get_aas_reference(self):
        aas_reference = model.ModelReference.from_referable(self.example_aas)
        retrieved_aas_reference = self.aasRepoClient.get_asset_administration_shell_by_id_reference_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"))
        # deserialization to model.Modelreference object is not happening
        self.CHECKER._check_reference_equal(retrieved_aas_reference, aas_reference)

    def test_put_and_get_aas(self):
        self.aasRepoClient.put_asset_administration_shell_by_id(
            body=self.example_aas_parsed, aas_identifier=string_to_base64url(
                "https://acplt.org/Test_AssetAdministrationShell"))
        retrieved_aas = self.aasRepoClient.get_asset_administration_shell_by_id(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"))
        self.CHECKER.check_asset_administration_shell_equal(retrieved_aas, self.example_aas)

    def test_put_and_get_aas_errors(self):
        self._assert_api_exception(
            lambda: self.aasRepoClient.put_asset_administration_shell_by_id(
                body=self.example_aas_parsed, aas_identifier="1"), 400, "Encoded data 1 is invalid base64url!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.put_asset_administration_shell_by_id(
                body=self.example_aas_parsed, aas_identifier="aHR0cHM6Ly9hY3BsdC5vcmc"), 404,
            "No AssetAdministrationShell with https://acplt.org found!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.put_asset_administration_shell_by_id(
                body="a", aas_identifier=string_to_base64url(
                    "https://acplt.org/Test_AssetAdministrationShell")), 422,
            "Object 'a' is not of type AssetAdministrationShell!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_asset_administration_shell_by_id(aas_identifier="1"), 400,
            "Encoded data 1 is invalid base64url!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_asset_administration_shell_by_id(aas_identifier="aHR0cHM6Ly9hY3BsdC5vcmc"),
            404, "No AssetAdministrationShell with https://acplt.org found!")

    def test_delete_and_post_aas(self):
        retrieved_aas = self.aasRepoClient.get_asset_administration_shell_by_id(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"))
        self.aasRepoClient.delete_asset_administration_shell_by_id(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"))
        retrieved_aas_parsed = AASClientTest._parse_object(object=retrieved_aas, encoder=AASToJsonEncoder)
        self.aasRepoClient.post_asset_administration_shell(retrieved_aas_parsed)
        retrieved_aas_new = self.aasRepoClient.get_asset_administration_shell_by_id(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"))
        self.CHECKER.check_asset_administration_shell_equal(retrieved_aas, retrieved_aas_new)

    def test_delete_and_post_aas_errors(self):
        retrieved_aas = self.aasRepoClient.get_asset_administration_shell_by_id(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"))

        self._assert_api_exception(
            lambda: self.aasRepoClient.delete_asset_administration_shell_by_id(aas_identifier="1"), 400,
            "Encoded data 1 is invalid base64url!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.delete_asset_administration_shell_by_id(
                aas_identifier="aHR0cHM6Ly9hY3BsdC5vcmc"), 404,
            "No AssetAdministrationShell with https://acplt.org found!")

        self.aasRepoClient.delete_asset_administration_shell_by_id(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"))
        retrieved_aas_parsed = AASClientTest._parse_object(object=retrieved_aas, encoder=AASToJsonEncoder)
        self.aasRepoClient.post_asset_administration_shell(retrieved_aas_parsed)

        self._assert_api_exception(
            lambda: self.aasRepoClient.post_asset_administration_shell("a"), 422,
            "Object 'a' is not of type AssetAdministrationShell!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.post_asset_administration_shell(retrieved_aas_parsed), 409,
            "AssetAdministrationShell with Identifier "
            "https://acplt.org/Test_AssetAdministrationShell already exists!")

    def test_put_and_get_asset_information(self):
        asset_information = self.example_aas_parsed.get('assetInformation', None)
        self.aasRepoClient.put_asset_information_aas_repository(
            body=asset_information, aas_identifier=string_to_base64url(
                "https://acplt.org/Test_AssetAdministrationShell"))
        retrieved_asset_information = self.aasRepoClient.get_asset_information_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"))
        self.CHECKER.check_asset_information_equal(retrieved_asset_information, self.example_aas.asset_information)

    def test_put_and_get_asset_information_errors(self):
        asset_information = self.example_aas_parsed.get('assetInformation', None)
        self._assert_api_exception(
            lambda: self.aasRepoClient.put_asset_information_aas_repository(body=asset_information, aas_identifier="1"),
            400, "Encoded data 1 is invalid base64url!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.put_asset_information_aas_repository(
                body=asset_information, aas_identifier="aHR0cHM6Ly9hY3BsdC5vcmc"), 404,
            "No AssetAdministrationShell with https://acplt.org found!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.put_asset_information_aas_repository(
                body="a", aas_identifier=string_to_base64url(
                    "https://acplt.org/Test_AssetAdministrationShell")), 422,
            "string indices must be integers, not 'str'")
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_asset_information_aas_repository(aas_identifier="1"), 400,
            "Encoded data 1 is invalid base64url!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_asset_information_aas_repository(aas_identifier="aHR0cHM6Ly9hY3BsdC5vcmc"),
            404, "No AssetAdministrationShell with https://acplt.org found!")

    # TODO: implement this once the deserialization problem of the model.Modelreference objects is fixed
    def test_get_delete_and_post_submodel_refs(self):
        submodel_references = self.aasRepoClient.get_all_submodel_references_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"))
        # deserialization to model.Modelreference object is not happening
        submodel_reference = submodel_references.result[0]
        submodel_reference.__class__ = model.ModelReference
        submodel_reference_dump = AASToJsonEncoder._reference_to_json(submodel_reference)
        submodel_reference_parsed = json.loads(submodel_reference_dump)
        submodel_id = submodel_reference_parsed.get('value', None)
        self.aasRepoClient.delete_submodel_reference_by_id_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(submodel_id))
        self.aasRepoClient.post_submodel_reference_aas_repository(
            body=submodel_reference_parsed, aas_identifier=string_to_base64url(
                "https://acplt.org/Test_AssetAdministrationShell"))

    def test_put_and_get_submodel(self):
        self.aasRepoClient.put_submodel_by_id_aas_repository(
            body=self.example_submodel_parsed, aas_identifier=string_to_base64url(
                "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier=string_to_base64url(
                self.example_submodel.id))
        retrieved_submodel = self.aasRepoClient.get_submodel_by_id_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id))
        self.CHECKER.check_submodel_equal(retrieved_submodel, self.example_submodel)

    def test_put_and_get_submodel_errors(self):
        self._assert_api_exception(
            lambda: self.aasRepoClient.put_submodel_by_id_aas_repository(
                body=self.example_submodel_parsed, aas_identifier=string_to_base64url(
                    "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier="1"), 400,
            "Encoded data 1 is invalid base64url!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.put_submodel_by_id_aas_repository(
                body=self.example_submodel_parsed, aas_identifier=string_to_base64url(
                    "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier="aHR0cD"), 404,
            "The AAS AssetAdministrationShell[https://acplt.org/Test_AssetAdministrationShell] doesn't"
            " have a submodel reference to 'http'!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.put_submodel_by_id_aas_repository(
                body="a", aas_identifier=string_to_base64url(
                    "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier=string_to_base64url(
                    self.example_submodel.id)), 422, "Object 'a' is not of type Submodel!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_submodel_by_id_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier="1"), 400, "Encoded data 1 is invalid base64url!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_submodel_by_id_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier="aHR0cD"), 404,
            "The AAS AssetAdministrationShell[https://acplt.org/Test_AssetAdministrationShell] "
            "doesn't"
            " have a submodel reference to 'http'!")

    def test_delete_submodel(self):
        self.aasRepoClient.get_submodel_by_id_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id))
        self.aasRepoClient.delete_submodel_by_id_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id))
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_submodel_by_id_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id)), 404,
            "The AAS AssetAdministrationShell[https://acplt.org/Test_AssetAdministrationShell] "
            "doesn't"
            f" have a submodel reference to {self.example_submodel.id!r}!")

    def test_delete_submodel_errors(self):
        self._assert_api_exception(
            lambda: self.aasRepoClient.delete_submodel_by_id_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier="1"), 400, "Encoded data 1 is invalid base64url!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.delete_submodel_by_id_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier="aHR0cD"), 404,
            "The AAS AssetAdministrationShell[https://acplt.org/Test_AssetAdministrationShell] "
            "doesn't"
            " have a submodel reference to 'http'!")

    def test_level(self):
        retrieved_submodel_core = self.aasRepoClient.get_submodel_by_id_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id), level="core")
        self.CHECKER.check_submodel_equal(retrieved_submodel_core, self.example_submodel_metadata)

    # TODO: implement this once the deserialization problem of the metadata is fixed
    def test_get_submodel_metadata(self):
        retrieved_submodel_metadata = self.aasRepoClient.get_submodel_by_id_metadata_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id))  # modelType is None, so Client can't
        # deserialize, modelType is correct in Insomnia. Problem with the way it is being deserialized
        self.CHECKER.check_submodel_equal(retrieved_submodel_metadata, self.example_submodel_metadata)

    # TODO: implement this once the deserialization problem of the metadata is fixed
    def test_get_submodel_metadata_errors(self):
        pass

    # TODO: implement this once the deserialization problem of the model.Modelreference objects is fixed
    def test_get_submodel_reference(self):
        submodel_reference = model.ModelReference.from_referable(self.example_submodel)
        retrieved_submodel_reference = self.aasRepoClient.get_submodel_by_id_reference_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id))
        # deserialization to model.Modelreference object is not happening
        self.CHECKER._check_reference_equal(retrieved_submodel_reference, submodel_reference)

    # TODO: implement this once the deserialization problem of the model.Modelreference objects is fixed
    def test_get_submodel_reference_errors(self):
        pass

    # TODO: implement this once the deserialization problem of some model.SubmodelElement objects is fixed
    def test_get_all_submodel_elements(self):
        retrieved_submodel_elements = self.aasRepoClient.get_all_submodel_elements_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id))
        # deserialization does not work for model.RelationshipElement
        submodel_element_list = retrieved_submodel_elements.result

    # TODO: implement this once the deserialization problem of some model.SubmodelElement objects is fixed
    def test_get_all_submodel_elements_errors(self):
        pass

    # TODO: implement this once the deserialization problem of some model.SubmodelElement objects is fixed
    def test_get_all_submodel_elements_metadata(self):
        retrieved_submodel_elements = self.aasRepoClient.get_all_submodel_elements_metadata_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id))
        # deserialization does not work for model.RelationshipElement
        submodel_element_list = retrieved_submodel_elements.result

    # TODO: implement this once the deserialization problem of some model.SubmodelElement objects is fixed
    def test_get_all_submodel_elements_metadata_errors(self):
        pass

    # TODO: implement this once the deserialization problem of the model.Modelreference objects is fixed
    def test_get_all_submodel_elements_references(self):
        retrieved_submodel_element_references = self.aasRepoClient.get_all_submodel_elements_reference_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id))  # deserialization is not happening

    # TODO: implement this once the deserialization problem of the model.Modelreference objects is fixed
    def test_get_all_submodel_elements_references_errors(self):
        pass

    # TODO: only works for some model.SubmodelElements
    def test_put_and_get_submodel_element(self):
        self.aasRepoClient.put_submodel_element_by_path_aas_repository(
            body=self.example_submodel_element_parsed, aas_identifier=string_to_base64url(
                "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier=string_to_base64url(
                self.example_submodel.id), id_short_path="ExampleSubmodelCollection")
        retrieved_submodel_element = self.aasRepoClient.get_submodel_element_by_path_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id),
            id_short_path="ExampleSubmodelCollection")
        self.CHECKER._check_submodel_element(retrieved_submodel_element, self.example_submodel_element)

    # TODO: only works for some model.SubmodelElements
    def test_put_and_get_submodel_element_errors(self):
        self._assert_api_exception(
            lambda: self.aasRepoClient.put_submodel_element_by_path_aas_repository(
                body=self.example_submodel_element_parsed,
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id), id_short_path="1"), 400,
            "1 is not a valid id_short!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.put_submodel_element_by_path_aas_repository(
                body=self.example_submodel_element_parsed,
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id), id_short_path="Example"), 404,
            "Referable with id_short Example not found in Submodel["
            "https://acplt.org/Test_Submodel]")
        self._assert_api_exception(
            lambda: self.aasRepoClient.put_submodel_element_by_path_aas_repository(
                body="a", aas_identifier=string_to_base64url(
                    "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier=string_to_base64url(
                    self.example_submodel.id), id_short_path="ExampleSubmodelCollection"), 422,
            "Object 'a' is not of type SubmodelElement!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_submodel_element_by_path_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id), id_short_path="1"), 400,
            "1 is not a valid id_short!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_submodel_element_by_path_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id), id_short_path="Example"), 404,
            "Referable with id_short Example not found in Submodel["
            "https://acplt.org/Test_Submodel]")

    # TODO: only works for some model.SubmodelElements
    def test_delete_and_post_submodel_element(self):
        retrieved_submodel_element = self.aasRepoClient.get_submodel_element_by_path_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id),
            id_short_path="ExampleSubmodelCollection")
        self.aasRepoClient.delete_submodel_element_by_path_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id),
            id_short_path="ExampleSubmodelCollection")
        retrieved_submodel_element_parsed = AASClientTest._parse_object(object=retrieved_submodel_element,
                                                                        encoder=AASToJsonEncoder)
        self.aasRepoClient.post_submodel_element_aas_repository(
            body=retrieved_submodel_element_parsed, aas_identifier=string_to_base64url(
                "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier=string_to_base64url(
                self.example_submodel.id))
        retrieved_submodel_element_new = self.aasRepoClient.get_submodel_element_by_path_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id),
            id_short_path="ExampleSubmodelCollection")
        self.CHECKER._check_submodel_element(retrieved_submodel_element, retrieved_submodel_element_new)

    # TODO: only works for some model.SubmodelElements
    def test_delete_and_post_submodel_element_errors(self):
        retrieved_submodel_element = self.aasRepoClient.get_submodel_element_by_path_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id),
            id_short_path="ExampleSubmodelCollection")

        self._assert_api_exception(
            lambda: self.aasRepoClient.delete_submodel_element_by_path_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id), id_short_path="1"), 400,
            "1 is not a valid id_short!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.delete_submodel_element_by_path_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id), id_short_path="Example"), 404,
            "Submodel element with id_short Example not found in Submodel["
            "https://acplt.org/Test_Submodel]")

        self.aasRepoClient.delete_submodel_element_by_path_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id),
            id_short_path="ExampleSubmodelCollection")
        retrieved_submodel_element_parsed = AASClientTest._parse_object(object=retrieved_submodel_element,
                                                                        encoder=AASToJsonEncoder)
        self.aasRepoClient.post_submodel_element_aas_repository(
            body=retrieved_submodel_element_parsed, aas_identifier=string_to_base64url(
                "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier=string_to_base64url(
                self.example_submodel.id))

        self._assert_api_exception(
            lambda: self.aasRepoClient.post_submodel_element_aas_repository(
                body="a", aas_identifier=string_to_base64url(
                    "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier=string_to_base64url(
                    self.example_submodel.id)), 422, "Object 'a' is not of type SubmodelElement!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.post_submodel_element_aas_repository(
                body=retrieved_submodel_element_parsed, aas_identifier=string_to_base64url(
                    "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier=string_to_base64url(
                    self.example_submodel.id)), 409,
            "SubmodelElement with idShort ExampleSubmodelCollection already exists"
            " within Submodel[https://acplt.org/Test_Submodel]!")

    # TODO: only works for some model.SubmodelElements
    def test_post_and_delete_submodel_element_in_submodel_element(self):
        retrieved_submodel_element = self.aasRepoClient.get_submodel_element_by_path_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id),
            id_short_path="ExampleSubmodelCollection")
        retrieved_submodel_element_parsed = AASClientTest._parse_object(object=retrieved_submodel_element,
                                                                        encoder=AASToJsonEncoder)
        self.aasRepoClient.post_submodel_element_by_path_aas_repository(
            body=retrieved_submodel_element_parsed, aas_identifier=string_to_base64url(
                "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier=string_to_base64url(
                self.example_submodel.id), id_short_path="ExampleSubmodelCollection")
        retrieved_submodel_element_new = self.aasRepoClient.get_submodel_element_by_path_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id),
            id_short_path="ExampleSubmodelCollection.ExampleSubmodelCollection")
        self.CHECKER._check_submodel_element(retrieved_submodel_element, retrieved_submodel_element_new)
        self.aasRepoClient.delete_submodel_element_by_path_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id),
            id_short_path="ExampleSubmodelCollection.ExampleSubmodelCollection")

    # TODO: only works for some model.SubmodelElements
    def test_post_submodel_element_in_submodel_element_errors(self):
        retrieved_submodel_element = self.aasRepoClient.get_submodel_element_by_path_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id),
            id_short_path="ExampleSubmodelCollection")
        retrieved_submodel_element_parsed = AASClientTest._parse_object(object=retrieved_submodel_element,
                                                                        encoder=AASToJsonEncoder)
        self.aasRepoClient.post_submodel_element_by_path_aas_repository(
            body=retrieved_submodel_element_parsed, aas_identifier=string_to_base64url(
                "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier=string_to_base64url(
                self.example_submodel.id), id_short_path="ExampleSubmodelCollection")
        self._assert_api_exception(
            lambda: self.aasRepoClient.post_submodel_element_by_path_aas_repository(
                body="a", aas_identifier=string_to_base64url(
                    "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier=string_to_base64url(
                    self.example_submodel.id), id_short_path="ExampleSubmodelCollection"), 422,
            "Object 'a' is not of type SubmodelElement!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.post_submodel_element_by_path_aas_repository(
                body=retrieved_submodel_element_parsed,
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id),
                id_short_path="ExampleSubmodelCollection"), 409,
            "SubmodelElement with idShort ExampleSubmodelCollection already exists within "
            "SubmodelElementCollection[https://acplt.org/Test_Submodel / "
            "ExampleSubmodelCollection]!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.delete_submodel_element_by_path_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id), id_short_path="1"), 400,
            "1 is not a valid id_short!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.delete_submodel_element_by_path_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id), id_short_path="Example"), 404,
            "Submodel element with id_short Example not found in Submodel["
            "https://acplt.org/Test_Submodel]")
        self.aasRepoClient.delete_submodel_element_by_path_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id),
            id_short_path="ExampleSubmodelCollection.ExampleSubmodelCollection")

    # TODO: implement this once the deserialization problem of the metadata is fixed
    def test_get_submodel_element_metadata(self):
        retrieved_submodel_element_metadata = self.aasRepoClient.get_submodel_element_by_path_metadata_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id),
            id_short_path="ExampleSubmodelCollection")
        self.CHECKER.check_submodel_equal(retrieved_submodel_element_metadata, self.example_submodel_metadata)

    # TODO: implement this once the deserialization problem of the model.Modelreference objects is fixed
    def test_get_submodel_element_reference(self):
        retrieved_submodel_element_reference = self.aasRepoClient.get_submodel_element_by_path_reference_aas_repository(
            aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
            submodel_identifier=string_to_base64url(self.example_submodel.id),
            id_short_path="ExampleSubmodelCollection")  # deserialization is not happening

    # TODO: implement this once the deserialization problem of the model.Modelreference objects is fixed
    def test_get_submodel_element_reference_errors(self):
        pass

    # TODO
    def test_put_and_get_submodel_element_attachment(self):
        # self.aasRepoClient.delete_file_by_path_aas_repository(
        #     aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
        #     submodel_identifier=string_to_base64url(self.example_submodel.id),
        #     id_short_path="ExampleSubmodelCollection.ExampleFile")
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            try:
                tmp_file_name = tmp_file.name
                self.aasRepoClient.put_file_by_path_aas_repository(
                    file_name="/empty_file.txt", file=tmp_file_name, aas_identifier=string_to_base64url(
                        "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier=string_to_base64url(
                        self.example_submodel.id), id_short_path="ExampleSubmodelCollection.ExampleFile")

            finally:
                tmp_file.close()
                os.remove(tmp_file_name)

    # TODO
    def test_put_and_get_submodel_element_attachment_errors(self):
        pass

    # TODO
    def test_delete_submodel_element_attachment(self):
        pass

    # TODO
    def test_delete_submodel_element_attachment_errors(self):
        pass

    def test_not_implemented(self):
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_thumbnail_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell")), 501,
            "This route is not implemented!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.delete_thumbnail_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell")), 501,
            "This route is not implemented!")
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            try:
                tmp_file_name = tmp_file.name

                self._assert_api_exception(
                    lambda: self.aasRepoClient.put_thumbnail_aas_repository(
                        file_name="empty_file.txt", file=tmp_file_name, aas_identifier=string_to_base64url(
                            "https://acplt.org/Test_AssetAdministrationShell")), 501, "This route is not implemented!")
            finally:
                tmp_file.close()
                os.remove(tmp_file_name)
        self._assert_api_exception(
            lambda: self.aasRepoClient.patch_submodel_aas_repository(
                body=self.example_submodel_parsed, aas_identifier=string_to_base64url(
                    "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier=string_to_base64url(
                    self.example_submodel.id)), 501, "This route is not implemented!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.patch_submodel_by_id_metadata_aas_repository(
                body=self.example_submodel_parsed, aas_identifier=string_to_base64url(
                    "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier=string_to_base64url(
                    self.example_submodel.id)), 501, "This route is not implemented!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_submodel_by_id_value_only_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id)), 501,
            "This route is not implemented!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_submodel_by_id_path_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id)), 501,
            "This route is not implemented!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_all_submodel_elements_value_only_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id)), 501,
            "This route is not implemented!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_all_submodel_elements_path_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id)), 501,
            "This route is not implemented!")
        id_short = self.example_submodel_parsed.get('idShort', None)
        self._assert_api_exception(
            lambda: self.aasRepoClient.patch_submodel_element_value_by_path_aas_repository(
                body=self.example_submodel_parsed,
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id),
                id_short_path=string_to_base64url(id_short)), 501, "This route is not implemented!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.patch_submodel_element_value_by_path_metadata(
                body=self.example_submodel_parsed, aas_identifier=string_to_base64url(
                    "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier=string_to_base64url(
                    self.example_submodel.id), id_short_path=string_to_base64url(
                    id_short)), 501, "This route is not implemented!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_submodel_element_by_path_value_only_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id),
                id_short_path=string_to_base64url(id_short)), 501, "This route is not implemented!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.patch_submodel_element_value_by_path_value_only(
                body=self.example_submodel_parsed,
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id),
                id_short_path=string_to_base64url(id_short)), 501, "This route is not implemented!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_submodel_element_by_path_path_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id),
                id_short_path=string_to_base64url(id_short)), 501, "This route is not implemented!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.invoke_operation_aas_repository(
                body=self.example_submodel_parsed, aas_identifier=string_to_base64url(
                    "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier=string_to_base64url(
                    self.example_submodel.id), id_short_path=string_to_base64url(id_short)), 501,
            "This route is not implemented!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.invoke_operation_value_only_aas_repository(
                body=self.example_submodel_parsed, aas_identifier=string_to_base64url(
                    "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier=string_to_base64url(
                    self.example_submodel.id), id_short_path=string_to_base64url(
                    id_short)), 501, "This route is not implemented!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.invoke_operation_async_aas_repository(
                body=self.example_submodel_parsed, aas_identifier=string_to_base64url(
                    "https://acplt.org/Test_AssetAdministrationShell"), submodel_identifier=string_to_base64url(
                    self.example_submodel.id), id_short_path=string_to_base64url(
                    id_short)), 501, "This route is not implemented!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.invoke_operation_async_value_only_aas_repository(
                body=self.example_submodel_parsed,
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id),
                id_short_path=string_to_base64url(id_short)), 501, "This route is not implemented!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_operation_async_status_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id),
                id_short_path=string_to_base64url(id_short), handle_id=string_to_base64url(self.example_submodel.id)),
            501, "This route is not implemented!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_operation_async_result_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id),
                id_short_path=string_to_base64url(id_short), handle_id=string_to_base64url(self.example_submodel.id)),
            501, "This route is not implemented!")
        self._assert_api_exception(
            lambda: self.aasRepoClient.get_operation_async_result_value_only_aas_repository(
                aas_identifier=string_to_base64url("https://acplt.org/Test_AssetAdministrationShell"),
                submodel_identifier=string_to_base64url(self.example_submodel.id),
                id_short_path=string_to_base64url(id_short), handle_id=string_to_base64url(self.example_submodel.id)),
            501, "This route is not implemented!")


if __name__ == "__main__":
    unittest.main()
