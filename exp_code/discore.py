# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2025 Andrzej Kaczmarczyk<droodev@gmail.com>
#
# The MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the “Software”), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class DistributionParameter(object):
    def __init__(self, name, value, ordinal_number):
        self._name = name
        self._value = value
        self._ordinal_number = ordinal_number

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def ordinal_number(self):
        return self._ordinal_number

    def __str__(self):
        return f"{self._ordinal_number} {self._name}: {self._value}"


class DistributionParameters(object):
    def __init__(self, **kwargs):
        self._distro_params_order = []
        for id_kwarg_pair in enumerate(kwargs.items()):
            new_param = DistributionParameter(
                id_kwarg_pair[1][0], id_kwarg_pair[1][1], id_kwarg_pair[0]
            )
            self._distro_params_order.append(new_param)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._distro_params_order[key]
        else:
            for distro_param in self._distro_params_order:
                if distro_param.name == key:
                    return distro_param
        raise KeyError(
            f"Key {key} is neither a name nor a valid index of any " "parameter"
        )

    def __str__(self):
        to_concat = []
        for param in self._distro_params_order:
            to_concat.append(str(param))
        return "\n".join(to_concat)

    def csv_header(self):
        return ",".join([param.name for param in self._distro_params_order])

    def csv_values(self):
        return ",".join([str(param.value) for param in self._distro_params_order])


class Distribution(object):

    def generate(self, votes_count, candidates=None):
        raise NotImplementedError("Should be overriden")

    def get_description(self):
        raise NotImplementedError("Should be overriden")


class ParameterizedDistribution(Distribution):

    def __init__(self, distribution_parameters):
        self._validate_parameters(distribution_parameters)
        self._assign_parameters(self._required_parameters, distribution_parameters)

    def _get_required_parameters(self):
        raise NotImplementedError("Should be overriden")

    _required_parameters = property(fget=lambda self: self._get_required_parameters())

    def _assign_parameters(self, param_names, parameters):
        absent_param = None
        self._parameters = parameters
        for param_name in param_names:
            try:
                code = f'self._{param_name} = parameters["{param_name}"].value'
                exec(code)
            except KeyError:
                absent_param = param_name
                break
        if absent_param:
            raise ValueError(f"Parameter {absent_param} required by {type(self)}")

    def _validate_parameters(self, parameters):
        all_present = True
        for param_name in self._required_parameters:
            try:
                parameters[param_name]
            except KeyError as keyError:
                raise ValueError(
                    "Arguments passed to the distribution do not conform to "
                    "the distribution's requirements: " + str(keyError)
                )
