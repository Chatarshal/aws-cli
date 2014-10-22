# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import json

from awscli.paramfile import get_paramfile
from awscli.argprocess import ParamError
from awscli.customizations.arguments import OverrideRequiredArgsArgument


def register_cli_input_json(cli):
    cli.register('building-argument-table', add_cli_input_json)


def add_cli_input_json(operation, argument_table, **kwargs):
    cli_input_json_argument = CliInputJSONArgument(operation)
    cli_input_json_argument.add_to_arg_table(argument_table)


class CliInputJSONArgument(OverrideRequiredArgsArgument):
    """This argument inputs a JSON string as the entire input for a command.

    Ideally, the value to this argument should be a filled out JSON file
    generated by ``--generate-cli-skeleton``. The items in the JSON string
    will not clobber other arguments entered into the command line.
    """
    ARG_DATA = {
        'name': 'cli-input-json',
        'help_text': 'Performs service operation based on the JSON string '
                     'provided. The JSON string follows the format provided '
                     'by ``--generate-cli-skeleton``. If other arguments are '
                     'provided on the command line, it will not clobber their '
                     'values.'
    }

    def __init__(self, operation_object):
        self._operation_object = operation_object
        super(CliInputJSONArgument, self).__init__(
            self._operation_object.session)

    def _register_argument_action(self):
        self._operation_object.session.register(
            'calling-service-operation', self.add_to_call_parameters)
        super(CliInputJSONArgument, self)._register_argument_action()

    def add_to_call_parameters(self, service_operation, call_parameters,
                               parsed_args, parsed_globals, **kwargs):

        # Check if ``--cli-input-json`` was specified in the command line.
        input_json = getattr(parsed_args, 'cli_input_json', None)
        if input_json is not None:
            # Retrieve the JSON from the file if needed.
            retrieved_json = get_paramfile(input_json)
            # Nothing was retrieved from the file. So assume the argument
            # is already a JSON string.
            if retrieved_json is None:
                retrieved_json = input_json
            try:
                # Try to load the JSON string into a python dictionary
                input_data = json.loads(retrieved_json)
            except ValueError as e:
                raise ParamError(
                    self.name, "Invalid JSON: %s\nJSON received: %s"
                    % (e, retrieved_json))
            # Add the members from the input JSON to the call parameters.
            self._update_call_parameters(call_parameters, input_data)

    def _update_call_parameters(self, call_parameters, input_data):
        for input_key in input_data.keys():
            # Only add the values to ``call_parameters`` if not already
            # present.
            if input_key not in call_parameters:
                call_parameters[input_key] = input_data[input_key]
