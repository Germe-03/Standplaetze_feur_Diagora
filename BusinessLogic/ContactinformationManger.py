from typing import List, Optional

from DataAccess.ContactInformationDataAccess import ContactInformationDataAccess
from DataAccess.UserDataAccess import UserDataAccess
from Model.ContactInformation import ContactInformation


class ContactinformationManger:
    def __init__(self, db_path: str = None):
        self.contact_information_dao = ContactInformationDataAccess(db_path)
        self.user_dao = UserDataAccess(db_path)

    def create_contact_information(self, email: str, phone: str, user_id: int) -> ContactInformation:
        """
        Erstellt eine neue Kontaktinformation mit Validierung der Geschäftsregeln
        """
        self._validate_contact_information_data(email, phone, user_id)

        user = self.user_dao.get_user_by_id(user_id)
        if not user:
            raise ValueError("Benutzer existiert nicht")

        existing_email_entries = self.contact_information_dao.get_contact_information_by_email(email.strip())
        if any(ci.user_id == user_id for ci in existing_email_entries):
            raise ValueError("Diese E-Mail ist für den Benutzer bereits vorhanden")

        return self.contact_information_dao.insert_contact_information(email.strip(), phone.strip(), user_id)

    def get_contact_information_by_id(self, contact_information_id: int) -> Optional[ContactInformation]:
        """
        Holt eine Kontaktinformation nach ID
        """
        if not contact_information_id or contact_information_id <= 0:
            raise ValueError("Ungültige ContactInformation-ID")
        return self.contact_information_dao.get_contact_information_by_id(contact_information_id)

    def get_contact_information_by_email(self, email: str) -> List[ContactInformation]:
        """
        Holt Kontaktinformationen per E-Mail
        """
        if not email or not email.strip():
            raise ValueError("E-Mail muss angegeben werden")
        return self.contact_information_dao.get_contact_information_by_email(email.strip())

    def get_contact_information_by_phone(self, phone: str) -> List[ContactInformation]:
        """
        Holt Kontaktinformationen per Telefon
        """
        if not phone or not phone.strip():
            raise ValueError("Telefon muss angegeben werden")
        return self.contact_information_dao.get_contact_information_by_phone(phone.strip())

    def get_contact_information_by_user(self, user_id: int) -> List[ContactInformation]:
        """
        Holt Kontaktinformationen eines Benutzers
        """
        if not user_id or user_id <= 0:
            raise ValueError("Ungültige User-ID")
        return self.contact_information_dao.get_contact_information_by_user_id(user_id)

    def get_contact_information_by_name(self, first_name: str, last_name: str) -> List[ContactInformation]:
        """
        Holt Kontaktinformationen per Benutzername
        """
        if not first_name or not first_name.strip():
            raise ValueError("Vorname muss angegeben werden")
        if not last_name or not last_name.strip():
            raise ValueError("Nachname muss angegeben werden")
        return self.contact_information_dao.get_contact_information_by_name(first_name.strip(), last_name.strip())

    def update_contact_information(self, contact_information: ContactInformation) -> None:
        """
        Aktualisiert eine bestehende Kontaktinformation
        """
        if not contact_information or not contact_information.contact_information_id:
            raise ValueError("Ungültige Kontaktinformation")

        existing_contact_information = self.contact_information_dao.get_contact_information_by_id(
            contact_information.contact_information_id
        )
        if not existing_contact_information:
            raise ValueError("Kontaktinformation existiert nicht")

        self.contact_information_dao.update_contact_information(contact_information)

    def delete_contact_information(self, contact_information_id: int) -> None:
        """
        Löscht eine Kontaktinformation
        """
        if not contact_information_id or contact_information_id <= 0:
            raise ValueError("Ungültige ContactInformation-ID")

        existing_contact_information = self.contact_information_dao.get_contact_information_by_id(contact_information_id)
        if not existing_contact_information:
            raise ValueError("Kontaktinformation existiert nicht")

        self.contact_information_dao.delete_contact_information(contact_information_id)

    def validate_contact_information_exists(self, contact_information_id: int) -> bool:
        """
        Prüft ob eine Kontaktinformation existiert
        """
        if not contact_information_id or contact_information_id <= 0:
            return False
        return self.contact_information_dao.get_contact_information_by_id(contact_information_id) is not None

    def _validate_contact_information_data(self, email: str, phone: str, user_id: int) -> None:
        """
        Validiert Kontaktinformation nach Geschäftsregeln
        """
        if not email or not email.strip():
            raise ValueError("E-Mail ist ein Pflichtfeld")
        if "@" not in email or "." not in email:
            raise ValueError("E-Mail hat kein gültiges Format")

        if not phone or not phone.strip():
            raise ValueError("Telefon ist ein Pflichtfeld")
        if len(phone.strip()) < 6:
            raise ValueError("Telefonnummer ist zu kurz")

        if not user_id or user_id <= 0:
            raise ValueError("Benutzer ist ein Pflichtfeld")
