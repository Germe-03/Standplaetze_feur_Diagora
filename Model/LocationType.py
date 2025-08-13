class LocationType:
    def __init__(self, location_type_id, location_type, user_id):
        self.__location_type_id = location_type_id
        self.__location_type = location_type
        self.__user_id = user_id

def __repr__(self):
    return (
        f"Location Type ID(id={self.__location_type_id!r}, Location Type={self.__location_type!r}, User ID={self.__user_id!r}")

@property
def location_type_id(self):
    return self.__location_type_id

@property
def location_type(self):
    return self.__location_type

@property
def user_id(self):
    return self.__user_id

@location_type.setter
def location_type(self, location_type):
    if not location_type:
        raise ValueError("Location Type must be set")
    if not isinstance(location_type, str):
        raise TypeError("Location Type must be a String")

@user_id.setter
def user_id(self, user_id):
    if not user_id:
        raise ValueError("User ID must be set")
    if not isinstance(user_id, int):
        raise TypeError("User ID must be a Int")