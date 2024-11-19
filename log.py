import config

def log(msg: str):
    '''
    prints `msg` to console if `config.DISABLE_LOG` is `False`
    '''
    if not config.DISABLE_LOG:
        print(msg)