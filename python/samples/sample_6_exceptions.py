"""
Sample 6: Exceptions

Demonstrates decorators for exception handling
"""

import sys
sys.path.append("..") # Add stk library to Python Path, if needed

import stk.runner
import stk.logging

class ALLoggerDemo(object):
    "Simple activity, demonstrating logging and exceptions"
    APP_ID = "com.aldebaran.example6"
    def __init__(self, qiapp):
        self.qiapp = qiapp
        self.logger = stk.logging.get_logger(qiapp.session, self.APP_ID)

    @stk.logging.log_exceptions
    def compute_arithmetic_quotient(self, num_a, num_b):
        "Do a complicated operation on the given numbers."
        return num_a / num_b

    @stk.logging.log_exceptions_and_return(False)
    def is_lucky(self, number):
        "Is this number lucky?"
        return (1.0 / number) < 0.5

    def stop(self):
        "Standard way of stopping the activity."
        self.qiapp.stop()

if __name__ == "__main__":
    stk.runner.run_service(ALLoggerDemo)
