# coding: utf-8

"""
    DotAAS Part 2 | HTTP/REST | Entire API Collection

    All APIs of the Specification of the [Specification of the Asset Administration Shell: Part 2](http://industrialdigitaltwin.org/en/content-hub) in one collection. Please not that this API is not intended to generate productive code but only for overview purposes.   Publisher: Industrial Digital Twin Association (IDTA) 2023\"  # noqa: E501

    OpenAPI spec version: V3.0.1
    Contact: info@idtwin.org
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class PackageDescription(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'aas_ids': 'list[str]',
        'package_id': 'str'
    }

    attribute_map = {
        'aas_ids': 'aasIds',
        'package_id': 'packageId'
    }

    def __init__(self, aas_ids=None, package_id=None):  # noqa: E501
        """PackageDescription - a model defined in Swagger"""  # noqa: E501
        self._aas_ids = None
        self._package_id = None
        self.discriminator = None
        if aas_ids is not None:
            self.aas_ids = aas_ids
        if package_id is not None:
            self.package_id = package_id

    @property
    def aas_ids(self):
        """Gets the aas_ids of this PackageDescription.  # noqa: E501


        :return: The aas_ids of this PackageDescription.  # noqa: E501
        :rtype: list[str]
        """
        return self._aas_ids

    @aas_ids.setter
    def aas_ids(self, aas_ids):
        """Sets the aas_ids of this PackageDescription.


        :param aas_ids: The aas_ids of this PackageDescription.  # noqa: E501
        :type: list[str]
        """

        self._aas_ids = aas_ids

    @property
    def package_id(self):
        """Gets the package_id of this PackageDescription.  # noqa: E501


        :return: The package_id of this PackageDescription.  # noqa: E501
        :rtype: str
        """
        return self._package_id

    @package_id.setter
    def package_id(self, package_id):
        """Sets the package_id of this PackageDescription.


        :param package_id: The package_id of this PackageDescription.  # noqa: E501
        :type: str
        """

        self._package_id = package_id

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(PackageDescription, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, PackageDescription):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
