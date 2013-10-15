WeBaCon
=======

'Cause who doesn't like bacon?

WeMo Basic Control - Allows one to issue basic commands to a WeMo unit via the command line.

Command line options
-------
```
-i <interface>
```
Specifies which interface to use.

```
-s <serial number>
```
Serial number of the WeMo.  If you don't specify this, you aren't going to control squat.

```
-c <status|on|off>
```
Sends the WeMo a command.  Possible commands are "status", "on", and "off".

```
-t <timeout>
```
Time out in seconds.  How long the script will wait before giving up on finding a device.  Default is 3.

```
-h
```
Shows the help.
