from DataAccess.BaseDataAccess import BaseDataAccess
from Model.ContactInformation import ContactInformation


class ContactInformationDataAccess(BaseDataAccess):
    def __init__(self, db_path: str = None):
        super().__init__(db_path)

    def get_contact_information_by_id(self, contact_information_id: int) -> ContactInformation | None:
        sql = """
        select ContactInformationID, E_Mail, Phone, UserID
        from ContactInformation
        where ContactInformationID = ?   
        """
        row = self.fetchone(sql, (contact_information_id,))
        if row:
            return ContactInformation(*row)
        return None

    def get_contact_information_by_email(self, email: str) -> list[ContactInformation]:
        sql = """
        select ContactInformationID, E_Mail, Phone, UserID
        from ContactInformation
        where E_Mail = ?
        """
        rows = self.fetchall(sql, (email,))
        return [ContactInformation(*row) for row in rows]

    def get_contact_information_by_phone(self, phone: str) -> list[ContactInformation]:
        sql = """
        select ContactInformationID, E_Mail, Phone, UserID
        from ContactInformation
        where Phone = ?
        """
        rows = self.fetchall(sql, (phone,))
        return [ContactInformation(*row) for row in rows]

    def get_contact_information_by_user_id(self, user_id: int) -> list[ContactInformation]:
        sql = """
        select ContactInformationID, E_Mail, Phone, UserID
        from ContactInformation
        where UserID = ?
        """
        rows = self.fetchall(sql, (user_id,))
        return [ContactInformation(*row) for row in rows]

    def get_contact_information_by_name(self, first_name: str, last_name: str) -> list[ContactInformation]:
        sql = """
        select ci.ContactInformationID, ci.E_Mail, ci.Phone, ci.UserID
        from ContactInformation ci
        join Users u on u.UserID = ci.UserID
        where u.FirstName = ? AND u.LastName = ?
        """
        rows = self.fetchall(sql, (first_name, last_name))
        return [ContactInformation(*row) for row in rows]

    def insert_contact_information(self, email: str, phone: str, user_id: int) -> ContactInformation:
        sql = """
        INSERT INTO ContactInformation (E_Mail, Phone, UserID)
        VALUES (?, ?, ?)
        """
        new_id, _ = self.execute(sql, (email, phone, user_id))
        return ContactInformation(new_id, email, phone, user_id)

    def update_contact_information(self, contact_information: ContactInformation) -> None:
        sql = """
        UPDATE ContactInformation
        SET E_Mail = ?, Phone = ?, UserID = ?
        WHERE ContactInformationID = ?
        """
        self.execute(sql, (contact_information.e_mail, contact_information.phone, 
                          contact_information.user_id, contact_information.contact_information_id))

    def delete_contact_information(self, contact_information_id: int) -> None:
        sql = "DELETE FROM ContactInformation WHERE ContactInformationID = ?"
        self.execute(sql, (contact_information_id,))
