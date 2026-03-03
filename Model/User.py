

class User:
    def __init__(self, user_id, last_name, first_name, password, role):
        self.__user_id = user_id
        self.__last_name = last_name
        self.__first_name = first_name
        self.__password = password
        self.__role = role

    def __repr__(self):
        return (f"User(id={self.__user_id!r}, Last Name={self.__last_name!r}, First Name={self.__first_name!r}"
                f"password={self.__password!r}), role={self.__role!r}")

    @property
    def user_id(self):
        return self.__user_id

    @property
    def last_name(self):
        return self.__last_name

    @last_name.setter
    def last_name(self, last_name):
        if not last_name:
            raise ValueError("Last Name is required")
        if not isinstance(last_name, str):
            raise TypeError("Last Name must be a string")
        self.__last_name = last_name


    @property
    def first_name(self):
        return self.__first_name

    @first_name.setter
    def first_name(self, first_name):
        if not first_name:
            raise ValueError("First Name is required")
        if not isinstance(first_name, str):
            raise TypeError("First Name must be a string")
        self.__first_name = first_name

    @property
    def password(self):
        return self.__password

    #TODO: Passwort voraussetzungen überarbeiten aktuell nur string
    @password.setter
    def password(self, password):
        if not password:
            raise ValueError("Password is required")
        if not isinstance(password, str):
            raise TypeError("Password must be a string")
        self.__password = password


    @property
    def role(self):
        return self.__role

    @role.setter
    def role(self, role):
        if not role:
            raise ValueError("Role is required")
        if not isinstance(role, str):
            raise TypeError("Role must be a string")
        self.__role = role
