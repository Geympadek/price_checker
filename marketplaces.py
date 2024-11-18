import wildberries, ozon

async def load_info(id: int, platform: str):
    '''
    Loads info about a product in dictionary
    '''
    if platform == "wildberries":
        return wildberries.load_info(id)
    if platform == "ozon":
        return await ozon.load_info(id)