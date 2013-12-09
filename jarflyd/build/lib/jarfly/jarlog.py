 #!/bin/env python

import syslog

def logit(pri, logentry):

    if pri == "INFO":
        syslog.syslog(syslog.LOG_INFO | syslog.LOG_DAEMON, logentry)

    if pri == "ERROR":
        print "Error: %s\n" % logentry
        syslog.syslog(syslog.LOG_ERR | syslog.LOG_DAEMON, logentry)



