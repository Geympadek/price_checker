TG_TOKEN = "token"
'''
Токен соответсвующего тг бота
'''

UPDATE_RATE = 3600
'''
Время между обновлением цен (секунды)
'''

PRODUCT_LIFETIME = 3600 * 24 * 7  #week
'''
Сколько секунд информация о товаре хранится в базе данных, если никто на него не подписан.
'''

DISABLE_LOG = False
'''
Включает или отключает вывод в консоль
'''

ITEMS_PER_PAGE = 8

DISABLE_UPDATE = False
'''
Выключает обновление информации о товарах (дебаг)
'''

CONTACT_LINK = "https://t.me/eellauu"
'''
Ссылка куда отправлять пользователей для баг репортов и отзывов
'''

RNN_PRICE_PERIOD = 3600 * 4
'''
На какие равные части поделить данные о цене (для машинного обучения, секунды)
'''