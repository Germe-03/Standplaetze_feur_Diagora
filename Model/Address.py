from pandas.io.stata import stata_epoch


class Address:
    def __init__(self, address_id:int, street:str, number:str, zip:str, city:str, state:str, user_id: int):
        self.__address_id = address_id
        self.__street = street
        self.__number = number
        self.__zip = zip
        self.__city = city
        self.__state = state
        self.__user_id = user_id

    def __repr__(self):
        return (f"Address(id={self.__address_id!r}, street={self.__street!r}, city={self.__number!r}, zip={self.__zip!r}"
                f"city={self.__city!r}), state={self.__state!r}, user={self.__user_id!r}")

    @property
    def address_id(self):
        return self.__address_id

    @property
    def street(self):
        return self.__street

    @street.setter
    def street(self, street):
        if not street:
            raise ValueError("street name is required")
        if not isinstance(street, str):
            raise TypeError("street must be a string")
        self.__street = street

    @property
    def city(self):
        return self.__city

    @city.setter
    def city(self, city):
        if not city:
            raise ValueError("city name is required")
        if not isinstance(city, str):
            raise TypeError("city must be a string")
        self.__city = city

    @property
    def zipe(self):
        return self.__zip

    @zip.setter
    def zip_code(self, zip_code):
        if not zip_code:
            raise ValueError("zip code is required")
        if not isinstance(zip_code, str):
            raise TypeError("zip code must be a string")
        self.__zip = zip

    @property
    def number(self):
        return self.__number

    @number.setter
    def number(self, number):
        if not number:
            raise ValueError("Value is required")
        if not isinstance(number, str):
            raise TypeError("number must be a string")

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, state):
        if not state:
            raise ValueError("State is required")
        if not isinstance(state, str):
            raise TypeError("State must be a string")

