# Communication from AR to AM for Silent-Hospital Use-Case
## Introduction

![](connection.png)

Assuming Silent-Hospital wants to build a Distributed Alarm System (DAS) according to 60601-1-8 we need to raise an alarm at both endpoints in case of communication failures.
In order to achieve this we need to check the connection between AM and AR periodically (in order to raise an alarm at the source device and at the communicator).
Also each alarm reported via PCD-04 message needs a timely response with a technical confirmation in order to keep the source device to not raise a technical condition indicating an alarm system failure.
The PCD-04 and PCD-05 messages are transported on different TCP sockets. The AR is opening a listening socket for PCD-04 message and the AM is opening a socket for PCD-05 messages. The port shall be.
## Requirements for Watchdog (aka Keep-Alive) Message
The current model is to send a PCD-04 message as a watchdog message (see Reference message 1). 

The AR expects this to be answered from the AM with an ACK message with MSA-1 segment containing the acknowledge code “CA” (see Reference message 2). 

It is expected that the ACK message is received on the same socket as the PCD-04 was sent.

The timeout for the ACK is specified by the AR in an OBX segment. The code (OBX-3) shall be 67860^MDC_ATTR_CONFIRM_TIMEOUT^MDC, the timeout is specified in OBX-5 with the unit in OBX-6

The default timeout for the ACK for the watchdog PCD-04 message is 5 seconds.

The watchdog message shall use the following code: MDC_EVT_WATCHDOG (CF-Code: TBD, for now: 0)

The watchdog message shall use an alarm state active and an inactivation state enabled while the device is connected to the AR. 

The watchdog message shall use the same location identifier and equipment ID as an alarm sourced from the device.

The watchdog message shall use the priority PN and the alert type SP

The watchdog message may provide the real patient information.

Once an AM receives a Watchdog message from AR it needs to check periodically for further watchdog messages and react accordingly if it does not come in. This could e.g. be a message to AC in order to alarm the user.

The AR shall send one last watchdog message with alarm state Inactive to indicate an intended shutdown of this alarm source. 


## Reference Messages
Reference messages can be found in the Reference folder of this repository
