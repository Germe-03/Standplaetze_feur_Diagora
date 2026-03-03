class Location:
    def __init__(self, location_id, name, is_sbb, max_dialog, rating, note, price, city_id, user_id):
        self.__location_id = location_id
        self.__name = name
        self.__is_sbb = is_sbb
        self.__max_dialog = max_dialog
        self.__rating = rating
        self.__note = note
        self.__price = price
        self.__city_id = city_id
        self.__user_id = user_id

    def __repr__(self):
        return (
            f"Location(id={self.__location_id!r}, Name={self.__name!r}, is SBB={self.__is_sbb!r}"
            f"max Dialog={self.__max_dialog!r}), rating={self.__rating!r}, nates={self.__note!r}, city_id={self.__city_id!r}"
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
    def rating(self):
        return self.__rating
    @property
    def note(self):
        return self.__note
    @property
    def price(self):
        return self.__price
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
        self.__name = name

    @is_sbb.setter
    def is_sbb(self, is_sbb):
        if not isinstance(is_sbb, bool):
            raise TypeError("SBB must be a Boolean")
        self.__is_sbb = is_sbb

    @max_dialog.setter
    def max_dialog(self, max_dialog):
        if not max_dialog:
            raise ValueError("Max Dialog is required")
        if not isinstance(max_dialog, int):
            raise TypeError("Max Dialog must be a Int")
        self.__max_dialog = max_dialog

    @rating.setter
    def rating(self, rating):
        if not rating:
            raise ValueError("Rating is required")
        if not isinstance(rating, int):
            raise TypeError("Rating must be a Integer")
        self.__rating = rating

    @note.setter
    def note(self, note):
        if note is not None and not isinstance(note, str):
            raise TypeError("Note must be a String")
        self.__note = note

    @price.setter
    def price(self, price):
        if price is not None and not isinstance(price, (int, float)):
            raise TypeError("Price must be a Float")
        self.__price = float(price) if price is not None else None

    @city_id.setter
    def city_id(self, city_id):
        if not city_id:
            raise ValueError("City ID is required")
        if not isinstance(city_id, int):
            raise TypeError("City ID must be a Int")
        self.__city_id = city_id

    @user_id.setter
    def user_id(self, user_id):
        if not user_id:
            raise ValueError("User ID is required")
        if not isinstance(user_id, int):
            raise TypeError("User ID must be a Int")
        self.__user_id = user_id


