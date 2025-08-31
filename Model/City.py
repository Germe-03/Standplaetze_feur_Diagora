

class City:
    def __init__(self, city_id, name, state_id):
        self.__city_id = city_id
        self.__name = name
        self.__state_id = state_id

        def __repr__(self):
            return (f"City(id={self.__city_id!r}, City Name={self.__name!r}, StateID={self.__state_id!r}")

    @property
    def city_id(self):
        return self.__city_id

    @property
    def name(self):
        return self.__name

    @property
    def state_id(self):
        return self.__state_id

    @name.setter
    def name(self, name):
        if not name:
            raise ValueError("Name is required")
        if not isinstance(name, str):
            raise TypeError("Name must be a string")

    @state_id.setter
    def state_id(self, state_id):
        if not state_id:
            raise ValueError("State ID is required")
        if not isinstance(state_id, int):
            raise TypeError("State ID must be an integer")