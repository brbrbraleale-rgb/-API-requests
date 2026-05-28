from abc import ABC, abstractmethod
from requests import get
import json
import os


class BaseAPI(ABC):
    """
    Абстрактный класс для работы с API.
    """

    @abstractmethod
    def get_aeroplanes(self, country: str) -> None:
        """Абстрактный метод для получения информации о самолетах."""
        pass


class APIAdapter(BaseAPI):
    """
    Класс, наследующийся от абстрактного класса, для работы с платформами
    nominatim.openstreetmap.org и opensky-network.org.
    """

    def __init__(self) -> None:
        self.openstreetmap_url = 'https://openstreetmap.org'
        self.opensky_url = 'https://opensky-network.org?'
        self.aeroplanes = None

    def get_aeroplanes(self, country: str) -> None:
        # Headers с user-agent - обязательный параметр при запросе к nominatim.openstreetmap.
        # Вы можете использовать любое название вместо test-app/1.0, например просто test-app.
        headers_nominatim = {
            'User-Agent': 'test-app/1.0',
        }

        # Указываем параметры: в каком формате возвращать данные и максимальную длину списка стран в ответе.
        params_nominatim = {
            'country': country,
            'format': 'json',
            'limit': 1,
        }

        response = get(url=self.openstreetmap_url, params=params_nominatim, headers=headers_nominatim)

        data = response.json()

        # Пример ответа от nominatim.openstreetmap можно посмотреть в задании курсовой.
        geo_coordinates = data[0].get('boundingbox')

        # Параметры для фильтрации самолетов по их географическим координатам.
        params = {
            'lamin': geo_coordinates[0],
            'lamax': geo_coordinates[1],
            'lomin': geo_coordinates[2],
            'lomax': geo_coordinates[3],
        }

        response = get(url=self.opensky_url, params=params)

        # Пример ответа от opensky-network можно посмотреть в задании курсовой.
        self.aeroplanes = response.json()


# класс для работы с самолётами

class Aeroplane:
    def __init__(self, callsign: str, origin_country: str, velocity: float, altitude: float) -> None:
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
    def cast_to_object_list(cls, raw_data: dict | list | None) -> list:
        """
        Преобразует ответ от OpenSky API в список объектов класса Aeroplane.
        """
        object_list = []
        if not raw_data:
            return object_list

        # Если передан весь JSON-ответ, извлекает из него список "states"
        if isinstance(raw_data, dict):
            states = raw_data.get("states", [])
        elif isinstance(raw_data, list):
            states = raw_data
        else:
            return object_list

        if not states:
            return object_list

        for state in states:
            try:
                # Извлекает параметры по индексам из ответа OpenSky:
                callsign = state[1]
                origin_country = state[2]
                altitude = state[7]
                velocity = state[9]

                # Создаёт объект самолета и добавляет его в итоговый список
                aeroplane_obj = cls(callsign, origin_country, velocity, altitude)
                object_list.append(aeroplane_obj)
            except (IndexError, TypeError):
                # Если в данных от API какой-то сбой, пропускает это
                continue

        return object_list

    # Реализация методов сравнения самолетов

    def __lt__(self, other: "Aeroplane") -> bool:
        """Сравнение 'меньше чем'по скорости, а при равенстве — по высоте"""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        if self.velocity != other.velocity:
            return self.velocity < other.velocity
        return self.altitude < other.altitude

    def __le__(self, other: "Aeroplane") -> bool:
        """Сравнение 'меньше или равно'"""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        if self.velocity != other.velocity:
            return self.velocity <= other.velocity
        return self.altitude <= other.altitude

    def __gt__(self, other: "Aeroplane") -> bool:
        """Сравнение 'больше чем'"""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        if self.velocity != other.velocity:
            return self.velocity > other.velocity
        return self.altitude > other.altitude

    def __ge__(self, other: "Aeroplane") -> bool:
        """Сравнение 'больше или равно'"""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        if self.velocity != other.velocity:
            return self.velocity >= other.velocity
        return self.altitude >= other.altitude

    def __eq__(self, other: "Aeroplane") -> bool:
        """Сравнение на равенство"""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.velocity == other.velocity and self.altitude == other.altitude

    def __repr__(self) -> str:
        """Вывод объекта на экран при печати списков"""
        return f"Aeroplane({self.callsign}, {self.origin_country}, V: {self.velocity} m/s, H: {self.altitude} m)"


class BaseSaver(ABC):
    """
    Абстрактный класс о самолетах.
    """
    @abstractmethod
    def add_aeroplane(self, aeroplane) -> None:
        pass

    @abstractmethod
    def get_aeroplanes_by_criteria(self, criteria: dict) -> list:
        pass

    @abstractmethod
    def delete_aeroplane(self, aeroplane) -> None:
        pass


class JSONSaver(BaseSaver):
    """
    Класс для сохранения информации о самолетах в JSON-файл.
    """
    def __init__(self, file_path: str = "data/aeroplanes.json") -> None:
        self.file_path = file_path

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Метод для добавления информации о самолете в файл."""
        data = []
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = []

        aeroplane_dict = {
            "callsign": aeroplane.callsign,
            "origin_country": aeroplane.origin_country,
            "velocity": aeroplane.velocity,
            "altitude": aeroplane.altitude
        }
        data.append(aeroplane_dict)

        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Метод для удаления информации о самолете."""
        if not os.path.exists(self.file_path):
            return

        with open(self.file_path, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                return

        data = [item for item in data if item.get("callsign") != aeroplane.callsign]

        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def get_aeroplanes_by_criteria(self, criteria: dict) -> list:
        pass