class Address:
    def __init__(self, address_id:int, street:str, number:str, zip:str, city:str, state_id:int, user_id: int):
        self.__address_id = address_id
        self.__street = street
        self.__number = number
        self.__zip = zip
        self.__city = city
        self.__state_id = state_id
        self.__user_id = user_id

    def __repr__(self):
        return (f"Address(id={self.__address_id!r}, street={self.__street!r}, number={self.__number!r}, zip={self.__zip!r}"
                f", city={self.__city!r}, state_id={self.__state_id!r}, user={self.__user_id!r}")

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
    def zip(self):
        return self.__zip

    @zip.setter
    def zip(self, zip_code):
        if not zip_code:
            raise ValueError("zip code is required")
        if not isinstance(zip_code, str):
            raise TypeError("zip code must be a string")
        self.__zip = zip_code

    @property
    def number(self):
        return self.__number

    @number.setter
    def number(self, number):
        if not number:
            raise ValueError("Value is required")
        if not isinstance(number, str):
            raise TypeError("number must be a string")
        self.__number = number

    @property
    def state_id(self):
        return self.__state_id

    @state_id.setter
    def state_id(self, state_id):
        if not state_id:
            raise ValueError("State ID is required")
        if not isinstance(state_id, int):
            raise TypeError("State ID must be an integer")
        self.__state_id = state_id

    @property
    def user_id(self):
        return self.__user_id

    @user_id.setter
    def user_id(self, user_id):
        if not user_id:
            raise ValueError("User ID is required")
        if not isinstance(user_id, int):
            raise TypeError("User ID must be an integer")
        self.__user_id = user_id


