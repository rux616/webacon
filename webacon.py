#!/usr/local/bin/python

##############################
#
# WeMo Basic Control (WeBaCon) by
# Dan Cassidy
# 2013-10-12
#
# Based on wemo.py by
# Isaac Kelly
# http://www.issackelly.com/
#
# Requires Miranda v1.4 by
# Craig Heffner
# https://code.google.com/p/miranda-upnp/
#
# Version:
# 1.0.1 (2013-10-18):
# - Changed the order of the functions
#
# 1.0 (2013-10-12):
# - Initial release
#
##############################

import sys
import getopt

# Requires Miranda v1.4
from miranda import upnp, msearch

# Show usage
def showusage():
	print "Usage: %s [OPTIONS]\n"\
		"  -i <interface>         Set interface\n"\
		"  -s <serial number>     Set serial number\n"\
		"  -c <status|on|off>     Send command to WeMo\n"\
		"  -t <seconds>           Set the timeout in seconds, default is 3\n"\
		"  -h                     Show help" % sys.argv[0]
	return

# Send request to a WeMo socket
def _send(hp, action, data=None):
    if not data:
        data = {}
    hostInfo = hp.ENUM_HOSTS[0]
    deviceName = 'controllee'
    serviceName = 'basicevent'
    controlURL = hostInfo['proto'] + hostInfo['name']
    controlURL2 = hostInfo['deviceList'][deviceName]['services'][serviceName]['controlURL']
    if not controlURL.endswith('/') and not controlURL2.startswith('/'):
        controlURL += '/'
    controlURL += controlURL2

    response = hp.sendSOAP(
        hostInfo['name'],
        'urn:Belkin:service:basicevent:1',
        controlURL,
        action,
        data
    )
    return response

# Gets the state of a WeMo socket
def get(hp):
    response = _send(hp, 'GetBinaryState')
    tagValue = hp.extractSingleTag(response, 'BinaryState')
    return True if tagValue == '1' else False

# Turns a WeMo socket on
def on(hp):
    # BinaryState is set to 'Error' in the case that it was already on.
    response = _send(hp, 'SetBinaryState', {'BinaryState': (1, 'Boolean')})
    tagValue = hp.extractSingleTag(response, 'BinaryState')
    return True if tagValue in ['1', 'Error'] else False

# Turns a WeMo socket off
def off(hp):
    # BinaryState is set to 'Error' in the case that it was already off.
    response = _send(hp, 'SetBinaryState', {'BinaryState': (0, 'Boolean')})
    tagValue = hp.extractSingleTag(response, 'BinaryState')
    return True if tagValue in ['0', 'Error'] else False

def main(argv):
	# Set defaults
	interface = None
	serialNumber = ""
	command = False
	timeout = 3

	# Check command line options
	try:
		opts, args = getopt.getopt(argv, "i:s:c:t:h")
	except getopt.GetoptError, e:
		print "Usage Error: ", e
		showusage()
		sys.exit(2)
	else:
		if opts == []:
			showusage()
			sys.exit(0)
		for opt, arg in opts:
			if opt in ("-i"):
				# interface
				interface = arg
			elif opt in ("-s"):
				# serial number
				serialNumber = arg
			elif opt in ("-c"):
				# command
				command = arg
			elif opt in ("-t"):
				# timeout
				timeout = int(arg)
			elif opt in ("-h"):
				# help
				showusage()
				sys.exit(0)

	# Create the connection
	hp = upnp(False, False, interface, None)

	# Update some of the connection settings
	hp.MAX_HOSTS = 1
	hp.TIMEOUT = timeout

	# Scan for the specified uuid
	msearch(3, ["msearch", "uuid", "Socket-1_0-%s" % serialNumber], hp)

	# Check to make sure that msearch found a device
	if len(hp.ENUM_HOSTS) == 0:
		# Device not found, die gracefully
		print "wemo: device_not_found"
		sys.exit(1)

	# Get the device's details
	hostInfo = hp.ENUM_HOSTS[0]
	if hostInfo['dataComplete'] == False:
		xmlHeaders, xmlData = hp.getXML(hostInfo['xmlFile'])
		hp.getHostInfo(xmlData,xmlHeaders,0)

	# Process command
	if command == "status":
		status = get(hp)
		if status:
			print "wemo: on"
		else:
			print "wemo: off"
		sys.exit(0)
	elif command == "off":
		status = off(hp)
		if status:
			print "wemo: off"
			sys.exit(0)
		else:
			print "wemo: error"
			sys.exit(1)
	elif command == "on":
		status = on(hp)
		if status:
			print "wemo: on"
			sys.exit(0)
		else:
			print "wemo: error"
			sys.exit(1)
	else:
		print "wemo: command_unknown"
		sys.exit(1)

if __name__ == "__main__":
	try:
		print "WeBaCon v1.0 by Dan Cassidy"
		main(sys.argv[1:])
	except Exception, e:
		print 'Caught main exception:',e
		sys.exit(1)