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

class RangeValue(object):
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
        'max': 'float',
        'min': 'float'
    }

    attribute_map = {
        'max': 'max',
        'min': 'min'
    }

    def __init__(self, max=None, min=None):  # noqa: E501
        """RangeValue - a model defined in Swagger"""  # noqa: E501
        self._max = None
        self._min = None
        self.discriminator = None
        self.max = max
        self.min = min

    @property
    def max(self):
        """Gets the max of this RangeValue.  # noqa: E501


        :return: The max of this RangeValue.  # noqa: E501
        :rtype: float
        """
        return self._max

    @max.setter
    def max(self, max):
        """Sets the max of this RangeValue.


        :param max: The max of this RangeValue.  # noqa: E501
        :type: float
        """
        if max is None:
            raise ValueError("Invalid value for `max`, must not be `None`")  # noqa: E501

        self._max = max

    @property
    def min(self):
        """Gets the min of this RangeValue.  # noqa: E501


        :return: The min of this RangeValue.  # noqa: E501
        :rtype: float
        """
        return self._min

    @min.setter
    def min(self, min):
        """Sets the min of this RangeValue.


        :param min: The min of this RangeValue.  # noqa: E501
        :type: float
        """
        if min is None:
            raise ValueError("Invalid value for `min`, must not be `None`")  # noqa: E501

        self._min = min

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
        if issubclass(RangeValue, dict):
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
        if not isinstance(other, RangeValue):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
