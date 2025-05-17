from widgets.LogWidget import ErrorLog

class LogManager:
    _instance = None
    
    def __new__(cls)-> ErrorLog:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.log = ErrorLog()
        return cls._instance

# Then in any file:
#from LogManager import LogManager
#LogManager().log.error("Global error message")