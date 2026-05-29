from abc import ABC, abstractmethod
from requests import get
import json
import os


class BaseAPI(ABC):
    """Абстрактный класс для работы с API (Принцип наследования)"""

    @abstractmethod
    def get_aeroplanes(self, country: str) -> list:
        pass


class AeroplanesAPI(BaseAPI):
    """
    Класс для работы с платформами nominatim и opensky-network.
    """

    def __init__(self) -> None:
        # много раз исправленный URL
        self.openstreetmap_url = 'https://nominatim.openstreetmap.org/search'
        self.opensky_url = 'https://opensky-network.org/api/states/all'
        self.auth = ("anastasia-api-client", "Pt6ciB.4k-FE-3S")
        self.aeroplanes = None

    def get_aeroplanes(self, country: str) -> list:
        # Изменяет User-Agent на уникальный, чтобы сервера не блокировали запросы
        headers_nominatim = {'User-Agent': 'MyUniqueEducationalPlaneTrackerApp/1.0'}
        params_nominatim = {'country': country, 'format': 'json', 'limit': 1}

        print(f"DEBUG: Отправляем запрос к Nominatim по адресу: {self.openstreetmap_url} с параметрами {params_nominatim}")

        response = get(url=self.openstreetmap_url, params=params_nominatim, headers=headers_nominatim, auth=self.auth)

        try:
            data = response.json()
        except Exception:
            print("Ошибка: Не удалось получить JSON от сервера OpenStreetMap.")
            return []

        if not data:
            print(f"Страна '{country}' не найдена в базе данных.")
            return []

        # Получает координаты из первого элемента списка
        geo_coordinates = data[0].get('boundingbox')
        if not geo_coordinates or len(geo_coordinates) < 4:
            print("Ошибка: Неверный формат координат от гео-сервера.")
            return []

        # Задаёт параметры для OpenSky. Ключи исправлены тоже"
        params = {
            'lamin': float(geo_coordinates[0]),
            'lamax': float(geo_coordinates[1]),
            'lomin': float(geo_coordinates[2]),
            'lomax': float(geo_coordinates[3]),
        }

        # Выполняет запрос к OpenSky
        response = get(url=self.opensky_url, params=params, auth=self.auth)

        # Проверяет статус ответа сервера перед чтением JSON
        if response.status_code != 200:
            print(f"Ошибка OpenSky API: Сервер вернул код {response.status_code}. Возможно, требуется авторизация.")
            self.aeroplanes = None
            return []

        try:
            self.aeroplanes = response.json()
        except Exception:
            print("Ошибка: OpenSky прислал некорректный ответ (не JSON).")
            self.aeroplanes = None
            return []

        # Возвращает список самолетов
        if self.aeroplanes and 'states' in self.aeroplanes and self.aeroplanes['states']:
            return self.aeroplanes['states']

        return []


class Aeroplane:
    def __init__(self, callsign: str, origin_country: str, velocity: float, altitude: float) -> None:
        # Инкапсуляция: валидация входных данных при инициализации
        self.callsign = str(callsign).strip() if callsign else "UNKNOWN"
        self.origin_country = str(origin_country).strip() if origin_country else "Unknown"

        try:
            self.velocity = float(velocity) if velocity is not None else 0.0
        except (ValueError, TypeError):
            self.velocity = 0.0

        try:
            self.altitude = float(altitude) if altitude is not None else 0.0
        except (ValueError, TypeError):
            self.altitude = 0.0

    @classmethod
    def cast_to_object_list(cls, raw_states: list) -> list:
        """Преобразование набора данных в список объектов."""
        object_list = []
        if not raw_states:
            return object_list

        for state in raw_states:
            try:
                callsign = state[1]
                origin_country = state[2]
                altitude = state[7]  # baro_altitude
                velocity = state[9]  # velocity

                object_list.append(cls(callsign, origin_country, velocity, altitude))
            except (IndexError, TypeError):
                continue
        return object_list

    # Магические методы сравнения по скорости и высоте полета
    def __lt__(self, other: "Aeroplane") -> bool:
        if self.velocity != other.velocity:
            return self.velocity < other.velocity
        return self.altitude < other.altitude

    def __eq__(self, other: "Aeroplane") -> bool:
        return self.velocity == other.velocity and self.altitude == other.altitude

    def __repr__(self) -> str:
        return f"Aeroplane({self.callsign}, {self.origin_country}, V: {self.velocity}, H: {self.altitude})"


class BaseSaver(ABC):
    """Абстрактный класс для хранилищ."""

    @abstractmethod
    def add_aeroplane(self, aeroplane) -> None: pass

    @abstractmethod
    def get_aeroplanes_by_criteria(self, criteria: dict) -> list: pass

    @abstractmethod
    def delete_aeroplane(self, aeroplane) -> None: pass


class JSONSaver(BaseSaver):
    """Класс для сохранения информации о самолетах в JSON-файл."""

    def __init__(self, file_path: str = "data/aeroplanes.json") -> None:
        self.file_path = file_path

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        data = []
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = []

        data.append({
            "callsign": aeroplane.callsign,
            "origin_country": aeroplane.origin_country,
            "velocity": aeroplane.velocity,
            "altitude": aeroplane.altitude
        })

        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        if not os.path.exists(self.file_path): return
        with open(self.file_path, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                return

        data = [item for item in data if item.get("callsign") != aeroplane.callsign]
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def get_aeroplanes_by_criteria(self, criteria: dict) -> list:
        """Заглушка"""
        pass
