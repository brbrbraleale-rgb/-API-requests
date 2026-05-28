from abc import ABC, abstractmethod
from requests import get

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
        self.openstreetmap_url = 'https://nominatim.openstreetmap.org/search'
        self.opensky_url = 'https://opensky-network.org/api/states/all?'
        self.aeroplanes = None

    def get_aeroplanes(self, country: str) -> None:
        #Headers с user-agent - обязательный параметр при запросе к nominatim.openstreetmap.
        #Вы можете использовать любое название вместо test-app/1.0, например просто test-app.
        headers_nominatim = {
            'User-Agent': 'test-app/1.0',
        }

        #Указываем параметры: в каком формате возвращать данные и максимальную длину списка стран в ответе.
        params_nominatim = {
            'country': country,
            'format': 'json',
            'limit': 1,
        }

        response = get(url=self.openstreetmap_url, params=params_nominatim, headers=headers_nominatim)

        data = response.json()

        #Пример ответа от nominatim.openstreetmap можно посмотреть в задании курсовой.
        geo_coordinates = data[0].get('boundingbox')

        #Параметры для фильтрации самолетов по их географическим координатам.
        params = {
            'lamin': geo_coordinates[0],
            'lamax': geo_coordinates[1],
            'lomin': geo_coordinates[2],
            'lomax': geo_coordinates[3],
        }

        response = get(url=self.opensky_url, params=params)

        #Пример ответа от opensky-network можно посмотреть в задании курсовой.
        self.aeroplanes = response.json()


if __name__ == "__main__":
    api = APIAdapter()
    api.get_aeroplanes('Canada')
