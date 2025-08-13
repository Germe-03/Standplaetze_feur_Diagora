class Location:
    def __init__(self, location_id, name, is_sbb, max_dialog, good, note, city_id, user_id):
        self.__location_id = location_id
        self.__name = name
        self.__is_sbb = is_sbb
        self.__max_dialog = max_dialog
        self.__good = good
        self.__note = note
        self.__city_id = city_id
        self.__user_id = user_id

    def __repr__(self):
        return (
            f"Location(id={self.__location_id!r}, Name={self.__name!r}, is SBB={self.__is_sbb!r}"
            f"max Dialog={self.__max_dialog!r}), good={self.__good!r}, nates={self.__note!r}, city_id={self.__city_id!r}"
            f"User ID={self.__user_id!r}")

    @property
    def location_id(self):
        return self.__location_id
    @property
    def name(self):
        return self.__name
    @property
    def is_sbb(self):
        return self.__is_sbb
    @property
    def max_dialog(self):
        return self.__max_dialog
    @property
    def good(self):
        return self.__good
    @property
    def note(self):
        return self.__note
    @property
    def city_id(self):
        return self.__city_id
    @property
    def user_id(self):
        return self.__user_id


    @name.setter
    def name(self, name):
        if not name:
            raise ValueError("Name is required")
        if not isinstance(name, str):
            raise TypeError("Name must be a String")

    @is_sbb.setter
    def is_sbb(self, is_sbb):
        if not is_sbb:
            raise ValueError("SBB is required")
        if not isinstance(is_sbb, bool):
            raise TypeError("SBB must be a Boolean")

    @max_dialog.setter
    def max_dialog(self, max_dialog):
        if not max_dialog:
            raise ValueError("Max Dialog is required")
        if not isinstance(max_dialog, int):
            raise TypeError("Max Dialog must be a Int")

    @good.setter
    def good(self, good):
        if not good:
            raise ValueError("Good is required")
        if not isinstance(good, bool):
            raise TypeError("Good must be a Boolean")

    @note.setter
    def note(self, note):
        if not note:
            raise ValueError("Note is required")
        if not isinstance(note, str):
            raise TypeError("Note must be a String")

    @city_id.setter
    def city_id(self, city_id):
        if not city_id:
            raise ValueError("City ID is required")
        if not isinstance(city_id, int):
            raise TypeError("City ID must be a Int")

    @user_id.setter
    def user_id(self, user_id):
        if not user_id:
            raise ValueError("User ID is required")
        if not isinstance(user_id, int):
            raise TypeError("User ID must be a Int")


