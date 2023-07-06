from configparser import ConfigParser
config_with_global = ConfigParser()
config_with_global.read('settings.ini')

API = config_with_global['API']
MYSQL = config_with_global['MYSQL']


# config_with_global = ConfigParser()
# config_with_global.read('settings.ini')


# filename_with_settings = 'settings.ini'

# config_with_global = ConfigParser()

# def create_config():
#     config_with_global.add_section('API')
#     host = port = user = password = database = None
#     host = input('Insert ip for API or press Enter (default 127.0.0.1)\n') or '127.0.0.1'
#     while not port:
#         port = input('Insert port for API (only digits and port >= 5000)\n')
#         if port.isdigit():
#             if int(port) < 5000:
#                 print('Port must be >= 5000')
#                 port = None
#         else:
#             print('Port must consist of digits')
#             port = None
#     config_with_global.set('API', 'host', host)
#     config_with_global.set('API', 'port', port)
#     config_with_global.set('API', 'debug', 'false')
#     config_with_global.set('API', 'ttl', '43200')
#     config_with_global.set('API', 'maxsize', '10000')
#     config_with_global.set('API', 'admin_ip', 'None')
#     config_with_global.set('API', 'control_key', 'None')


#     config_with_global.add_section('local')
#     config_with_global.set('local', 'user', user)
#     config_with_global.set('local', 'password', password)
#     config_with_global.set('local', 'database', database)

#     def request_data_for_db():
#         nonlocal user, password, database
#         user = password = database = None
#         while not database:
#             database = input('Insert name database on MySQL\n')
#         while not user:
#             user = input('Insert username with ALL_PRIVILEGES on MySQL\n')
#         while not password:
#             password = input(f'Insert password for "{user}" \n')
#         return user, password, database


#     config_with_global.add_section('local')
#     config_with_global.set('local', 'user', user)
#     config_with_global.set('local', 'password', password)
#     config_with_global.set('local', 'database', database)

#     with open(filename_with_settings, 'w') as config_file:
#         config_with_global.write(config_file)




# if not path.isfile(filename_with_settings):
#     create_config()
# else:
#     config_with_global.read(filename_with_settings)


# API = config_with_global['API']
# MYSQL_ECHO = config_with_global['local'].getboolean('echo_param')