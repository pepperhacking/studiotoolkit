"""
Sample 2: using robot_services.ServiceCache for simply accessing services.

ALAddition is created in example 4, you can try this with and without running
it first.
"""

import sys
sys.path.append("..") # Add stk library to Python Path, if needed

import stk.runner
import stk.services

if __name__ == "__main__":
    qiapp = stk.runner.init()
    services = stk.services.ServiceCache(qiapp.session)

    if services.ALAddition:
        result = services.ALAddition.add(2, 2)
        services.ALTextToSpeech.say("2 and 2 are " + str(result))
    else:
        services.ALTextToSpeech.say("ALAddition not found, so watch my eyes")
        services.ALLeds.rasta(2.0)
