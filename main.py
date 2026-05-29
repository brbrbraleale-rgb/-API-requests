"""Классы и методы"""
from src.api import AeroplanesAPI, Aeroplane, JSONSaver

def filter_aeroplanes(aeroplanes_list: list, filter_words: list) -> list:
    """Фильтрует список самолетов по странам регистрации."""
    if not filter_words:
        return aeroplanes_list
    words_lower = [w.lower() for w in filter_words]
    return [p for p in aeroplanes_list if p.origin_country.lower() in words_lower]


def get_aeroplanes_by_altitude(aeroplanes_list: list, altitude_range: str) -> list:
    """Фильтрует список самолетов по диапазону высот полета."""
    if not altitude_range or '-' not in altitude_range:
        return aeroplanes_list
    try:
        start, end = altitude_range.split('-')
        min_alt = float(start.strip())
        max_alt = float(end.strip())
        return [p for p in aeroplanes_list if min_alt <= p.altitude <= max_alt]
    except (ValueError, TypeError):
        return aeroplanes_list


def sort_aeroplanes(aeroplanes_list: list) -> list:
    """Сортирует список самолетов (например, по высоте или скорости)"""
    return sorted(aeroplanes_list, reverse=True)


def get_top_aeroplanes(aeroplanes_list: list, top_n: int) -> list:
    """ Возвращает первые N самолетов из списка."""
    return aeroplanes_list[:top_n]


def print_aeroplanes(aeroplanes_list: list) -> None:
    """Выводит информацию о самолетах в консоль в форматированном виде."""
    if not aeroplanes_list:
        print("Самолеты не найдены.")
        return
    for i, p in enumerate(aeroplanes_list, start=1):
        print(f"{i}. {p.callsign} ({p.origin_country}) -> Высота: {p.altitude}м, Скорость: {p.velocity}м/с")


# Функция для взаимодействия с пользователем
def user_interaction():
    """Организует взаимодействие с пользователем: запрашивает данные и выводит топ самолетов"""
    api = AeroplanesAPI()
    raw_data = api.get_aeroplanes('Spain')
    aeroplanes = Aeroplane.cast_to_object_list(raw_data)

    aeroplane = Aeroplane("UAL1621", "United States", 268.79, 10203.18)

    json_saver = JSONSaver()
    json_saver.add_aeroplane(aeroplane)
    json_saver.delete_aeroplane(aeroplane)

    country = input("Введите название страны: ")
    top_n = int(input("Введите количество самолетов для вывода в топ N: "))
    filter_words = input("Введите названия стран для фильтрации по стране регистрации: ").split()
    altitude_range = input("Введите диапазон высот полета: ")

    # Повторный запрос данных по выбранной пользователем стране
    user_raw = api.get_aeroplanes(country)
    user_aeroplanes = Aeroplane.cast_to_object_list(user_raw)

    filtered_aeroplanes = filter_aeroplanes(user_aeroplanes, filter_words)
    ranged_aeroplanes = get_aeroplanes_by_altitude(filtered_aeroplanes, altitude_range)
    sorted_aeroplanes = sort_aeroplanes(ranged_aeroplanes)
    top_aeroplanes = get_top_aeroplanes(sorted_aeroplanes, top_n)
    print_aeroplanes(top_aeroplanes)


if __name__ == "__main__":
    user_interaction()

