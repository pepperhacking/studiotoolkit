"""
Sample 4: A simple NAOqi service.

Once it's launched, you can call ALAddition.add(1, 2) on the robot
(for example, with qicli).

Docstrings will be shown in qicli info ALAddition --show-doc.
"""

import sys
sys.path.append("..") # Add stk library to Python Path, if needed

import qi
import stk.runner

class ALAddition(object):
    "Powerful arithmetic service."
    def __init__(self, qiapplication):
        self.qiapplication = qiapplication

    @qi.bind(qi.Int32, [qi.Int32, qi.Int32])
    def add(self, num_a, num_b):
        "Returns the sum of two numbers"
        return num_a + num_b

    @qi.bind(qi.Void, [])
    def stop(self):
        "Stops the service"
        self.qiapplication.stop()

if __name__ == "__main__":
    stk.runner.run_service(ALAddition)
