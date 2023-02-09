import logging
import os

class privateLogger(logging.Logger):
    def __init__(self, title='Log',Folder=os.getcwd(),DateRef:bool=False,level=logging.NOTSET, name: str='Marsh') -> None:
        super().__init__(name, level)
        if DateRef:
            import datetime
            today=datetime.datetime.today().strftime('_%Y_%m_%d_%f')
        else:
            today=''
        if os.path.isdir(Folder):
            logPath=os.path.join(
                Folder,
                f'{title}{today}.log'
            )

        file_handler=logging.FileHandler(logPath,mode='w+')
        file_handler.setLevel(logging.INFO)
        f_format = logging.Formatter('%(name)s | %(asctime)s | %(levelname)s | %(message)s')
        file_handler.setFormatter(f_format)
        
        console_handler=logging.StreamHandler()
        console_handler.setLevel(logging.NOTSET)
        f_format = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(f_format)
        
        self.addHandler(console_handler)
        self.addHandler(file_handler)