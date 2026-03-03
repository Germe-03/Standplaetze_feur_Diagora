

class ContactInformation:
    def __init__(self, contact_information_id, e_mail, phone, user_id):
        self.__contact_information_id = contact_information_id
        self.__e_mail = e_mail
        self.__phone = phone
        self.__user_id = user_id


    def __repr__(self):
        return (f"Contact information(id={self.__contact_information_id!r}, E-Mail={self.__e_mail!r}"
                f"phone={self.__phone!r}), user ID={self.__user_id!r}")

    @property
    def contact_information_id(self):
        return self.__contact_information_id

    @property
    def e_mail(self):
        return self.__e_mail

    @e_mail.setter
    def e_mail(self, e_mail):
        if not e_mail:
            raise ValueError("E-Mail is required")
        if not isinstance(e_mail, str):
            raise TypeError("E-Mail must be a string")
        self.__e_mail = e_mail


    @property
    def phone(self):
        return self.__phone

    @phone.setter
    def phone(self, phone):
        if not isinstance(phone, str):
            raise TypeError("Phone must be a string")
        if not phone:
            raise ValueError("Phone is required")
        self.__phone = phone

    @property
    def user_id(self):
        return self.__user_id

    @user_id.setter
    def user_id(self, user_id):
        if not user_id:
            raise ValueError("User ID is required")
        if not isinstance(user_id, int):
            raise TypeError("User ID must be a Integer")
        self.__user_id = user_id
