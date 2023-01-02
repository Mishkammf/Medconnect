
import json
import os

from common.singleton import Singleton


class MissingConfigException(Exception):
    """
    Required configuration parameter is not specified in default_config.json
    """

    def __init__(self, key):
        self.message = "Missing configuration: %s" % key


def get_config(key):
    return ConfigManager.instance().get(key)


config_file_name = "default_config.json"


@Singleton
class ConfigManager:
    """
    Obtain configurations of a project_id. The configurations are read from the json file specified in CONFIG_FILE
    environment variable.
        E.g.
        {
          "thread_pool": {
            "thread_count": 20
          }
        }

    The configuration fields read from CONFIG_FILE can be override using environment variables set to match field key.
        E.g. An environment variable THREAD_POOL.THREAD_COUNT=30 would override the thread_count field specified
        in config json file.
    """

    def __init__(self):
        """
        Constructor
        """
        global config_file_name
        if "CONFIG_FILE" in os.environ:
            config_file_name = os.environ["CONFIG_FILE"]

        with open(config_file_name, "r") as f:
            str_config = f.read()
            self.config_dict = json.loads(str_config)

    def get(self, key):
        """
        Obtain a configuration value using a hierarchic key specified in period (.) separated manner.
            E.g.: thread_pool.thread_count
        :param key: Period (.) separated key
        :return:
        """
        # First check env variable overrides
        if key.upper() in os.environ:
            return os.environ[key.upper()]

        # If not, read from config file
        parts = key.split(".")
        current = self.config_dict
        for part in parts:
            if part in current:
                current = current[part]
            else:
                raise MissingConfigException(key)
        return current
