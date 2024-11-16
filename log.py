import config

def log(msg: str):
    if not config.DISABLE_LOG:
        print(msg)