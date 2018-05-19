# Server has to be run in current time to enable proper handling of google accounts authentication
# This script should be run in test environment before main.py
# In PyCharm insert it as external tool in before launch in Execution Configuration
import ntplib
from time import ctime
import sys

connection = ntplib.NTPClient()
response = connection.request('time.google.com', version=3)
if response.offset > 600:
    # Time offset for proper authentication can be grater then 600 seconds(10 minutes)
    # but its bad enough if the server is 10 minutes late
    sys.stderr.write('This server has bad Date&Time settings:\n' +
                     'Offset: ' + str(response.offset) + '\n' +
                     'Server time: ' + ctime() + '\n' +
                     'Proper time: ' + ctime(response.tx_time) + '\n' +
                     'Please fix time on server and run again')
    sys.exit(1)
