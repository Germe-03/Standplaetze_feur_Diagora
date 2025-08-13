

class City:
    def __init__(self, city_id, name, state):
        self.__city_id = city_id
        self.__name = name
        self.__state = state

        def __repr__(self):
            return (f"City(id={self.__city!r}, City Name={self.__name!r}, State={self.__state!r}")

    @property
    def city_id(self):
        return self.__city_id

    @property
    def name(self):
        return self.__name

    @property
    def state(self):
        return self.__state

    @name.setter
    def name(self, name):
        if not name:
            raise ValueError("Name is required")
        if not isinstance(name, str):
            raise TypeError("Name must be a string")

    @state.setter
    def state(self, state):
        if not state:
            raise ValueError("State is required")
        if not isinstance(state, str):
            raise TypeError("State must be a string")