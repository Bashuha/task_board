from configparser import ConfigParser
import toml


config_with_global = ConfigParser()
config_with_global.read('settings.ini')
cuurent_config = toml.load('test_settings.toml')


API = config_with_global['API']
MYSQL = config_with_global['MYSQL']
JWT = config_with_global['JWT']
TEST_DB = cuurent_config['TEST_DB']