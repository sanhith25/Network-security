import sys

class NetworkSecurityException(Exception):
    def __init__(self, error_message, error_details: sys):
        _, _, exc_tb = error_details.exc_info()
        
        if isinstance(error_message, Exception):
            self.error_message = str(error_message)
        else:
            self.error_message = str(error_message)
        
        if exc_tb:
            self.lineno = exc_tb.tb_lineno
            self.file_name = exc_tb.tb_frame.f_code.co_filename
        else:
        
            self.lineno = "N/A"
            self.file_name = "N/A"
    
    def __str__(self):
        return f"Error occurred in python script [{self.file_name}] line number [{self.lineno}] - {self.error_message}"
