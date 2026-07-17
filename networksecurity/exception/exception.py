import sys
from networksecurity.logging import logger


class NetworkSecurityException(Exception):

    def __init__(self, error_message: Exception, error_details: sys):

        super().__init__(str(error_message))

        _, _, exc_tb = error_details.exc_info()

        if exc_tb is not None:
            self.file_name = exc_tb.tb_frame.f_code.co_filename
            self.line_number = exc_tb.tb_lineno
            self.function_name = exc_tb.tb_frame.f_code.co_name
        else:
            self.file_name = "Unknown"
            self.line_number = 0
            self.function_name = "Unknown"

        self.error_message = str(error_message)

    def __str__(self):

        return f"""
==============================
Network Security Exception
==============================
File Name      : {self.file_name}
Function Name  : {self.function_name}
Line Number    : {self.line_number}
Error Message  : {self.error_message}
==============================
"""


if __name__ == "__main__":

    try:

        logger.info("Starting exception testing")

        a = 1 / 0

    except Exception as e:

        raise NetworkSecurityException(e, sys)