class State:
    def __init__(self, state_id, name):
        self.__state_id = state_id
        self.__name = name

    def __repr__(self):
        return f"State(id={self.__state_id!r}, Name={self.__name!r})"

    @property
    def state_id(self):
        return self.__state_id

    @property
    def name(self):
        return self.__name

    @state_id.setter
    def state_id(self, state_id):
        if not state_id:
            raise ValueError("State ID is required")
        if not isinstance(state_id, int):
            raise TypeError("State ID must be an integer")
        self.__state_id = state_id

    @name.setter
    def name(self, name):
        if not name:
            raise ValueError("Name is required")
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        self.__name = name

