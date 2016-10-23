import os
import configparser


class ConfigValidator(object):
    def __init__(self, config_file=None):
        self.config_file = config_file
        self.expected_config = []
        self.config = []
        self._parser = configparser.ConfigParser()

        if not os.path.isfile(self.config_file):
            raise FileNotFoundError("No such file or directory: " + self.config_file)

        self._parser.read(config_file)

        if not self._parser.sections():
            raise ImportError("No sections found in config file: " + self.config_file)

    def add_option(self, option=None, required=False, valid_values=[], default_value=None):
        if not option:
            raise ImportError('Option value is needed')

        template ={
            "option": option,
            "required": required,
            "valid_values": valid_values,
            "default_value": default_value
        }
        self.expected_config.append(template)

    def add_selection(self, options=[], required=False, valid_values=[], default_value=None, default_option=None):
        if not options:
            raise ImportError('Option value is needed')

        template ={
            "options": options,
            "required": required,
            "valid_values": valid_values,
            "default_value": default_value,
            "default_option": default_option
        }
        self.expected_config.append(template)

    def validate(self):
        for section in self._parser.sections():
            validated_section = {'SectionName': section}
            for config in self.expected_config:
                validated_option = None
                validated_value = None

                if "options" in config:
                    for option in config["options"]:
                        if self._parser.has_option(section, option):
                            validated_option = option
                            valid_values = config["valid_values"]
                            section_value = self._parser[section][option]

                            if not valid_values:
                                if section_value:
                                    validated_value = section_value
                                    break
                                elif config['default_value']:
                                    validated_value = config['default_value']
                                    break

                            elif section_value in valid_values:
                                validated_value = section_value
                                break
                            else:
                                raise ValueError('The specified value is not allowed: ' + option + ': ' + section_value)

                    if not validated_option and config['default_option']:
                        validated_option = config['default_option']

                    if not validated_value and config['default_value']:
                        validated_value = config['default_value']

                    if not validated_option and not validated_value:
                        if config['default_value'] and config['default_option']:
                            validated_option = config['default_option']
                            validated_value = config['default_value']

                else:
                    option = config["option"]
                    if self._parser.has_option(section, option):
                        validated_option = option
                        valid_values = config["valid_values"]
                        section_value = self._parser[section][option]

                        if not valid_values:
                            if section_value:
                                validated_value = section_value
                            elif config['default_value']:
                                validated_value = config['default_value']

                        elif section_value in valid_values:
                            validated_value = section_value

                        else:
                            raise ValueError('The specified value is not allowed: ' + option + ': ' + section_value)

                    elif config['default_value']:
                        validated_option = option
                        validated_value = config['default_value']

                if validated_value and validated_option:
                    validated_section.update(
                        {validated_option: validated_value}
                    )
                elif config["required"]:
                    invalid_opt = str(config["option"]) if "option" in config else str(config["options"])
                    raise ValueError("Missing required configuration: " + invalid_opt)
            self.config.append(validated_section)
