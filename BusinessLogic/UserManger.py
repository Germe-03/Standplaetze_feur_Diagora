from typing import List, Optional

from DataAccess.UserDataAccess import UserDataAccess
from Model.User import User


class UserManger:
    def __init__(self, db_path: str = None):
        self.user_dao = UserDataAccess(db_path)

    def create_user(self, last_name: str, first_name: str, password: str, role: str) -> User:
        """
        Erstellt einen neuen Benutzer mit Validierung der Geschäftsregeln
        """
        self._validate_user_data(last_name, first_name, password, role)

        existing_users = self.user_dao.get_user_by_name(first_name.strip(), last_name.strip())
        if existing_users:
            raise ValueError("Ein Benutzer mit diesem Namen existiert bereits")

        return self.user_dao.insert_user(last_name.strip(), first_name.strip(), password, role.strip())

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Holt einen Benutzer nach ID
        """
        if not user_id or user_id <= 0:
            raise ValueError("Ungültige User-ID")
        return self.user_dao.get_user_by_id(user_id)

    def get_user_by_name(self, first_name: str, last_name: str) -> List[User]:
        """
        Holt Benutzer anhand von Vor- und Nachname
        """
        if not first_name or not first_name.strip():
            raise ValueError("Vorname muss angegeben werden")
        if not last_name or not last_name.strip():
            raise ValueError("Nachname muss angegeben werden")
        return self.user_dao.get_user_by_name(first_name.strip(), last_name.strip())

    def get_users_by_first_name(self, first_name: str) -> List[User]:
        """
        Holt Benutzer nach Vorname
        """
        if not first_name or not first_name.strip():
            raise ValueError("Vorname muss angegeben werden")
        return self.user_dao.get_users_by_first_name(first_name.strip())

    def get_users_by_last_name(self, last_name: str) -> List[User]:
        """
        Holt Benutzer nach Nachname
        """
        if not last_name or not last_name.strip():
            raise ValueError("Nachname muss angegeben werden")
        return self.user_dao.get_users_by_last_name(last_name.strip())

    def get_users_by_role(self, role: str) -> List[User]:
        """
        Holt Benutzer nach Rolle
        """
        if not role or not role.strip():
            raise ValueError("Rolle muss angegeben werden")
        return self.user_dao.get_users_by_role(role.strip())

    def search_users_by_name_pattern(self, name_pattern: str) -> List[User]:
        """
        Sucht Benutzer nach Teilstring in Vor- oder Nachname
        """
        if not name_pattern or not name_pattern.strip():
            raise ValueError("Suchmuster muss angegeben werden")
        return self.user_dao.get_users_by_name_pattern(name_pattern.strip())

    def get_all_users(self) -> List[User]:
        """
        Holt alle Benutzer
        """
        return self.user_dao.get_all_users()

    def authenticate_user(self, first_name: str, last_name: str, password: str) -> Optional[User]:
        """
        Authentifiziert einen Benutzer
        """
        if not first_name or not first_name.strip():
            raise ValueError("Vorname muss angegeben werden")
        if not last_name or not last_name.strip():
            raise ValueError("Nachname muss angegeben werden")
        if not password:
            raise ValueError("Passwort muss angegeben werden")

        return self.user_dao.authenticate_user(first_name.strip(), last_name.strip(), password)

    def update_user(self, user: User) -> None:
        """
        Aktualisiert einen bestehenden Benutzer
        """
        if not user or not user.user_id:
            raise ValueError("Ungültiger Benutzer")

        existing_user = self.user_dao.get_user_by_id(user.user_id)
        if not existing_user:
            raise ValueError("Benutzer existiert nicht")

        self.user_dao.update_user(user)

    def update_user_password(self, user_id: int, new_password: str) -> None:
        """
        Aktualisiert das Passwort eines Benutzers
        """
        if not user_id or user_id <= 0:
            raise ValueError("Ungültige User-ID")
        if not new_password or len(new_password) < 4:
            raise ValueError("Neues Passwort ist ungültig")

        existing_user = self.user_dao.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError("Benutzer existiert nicht")

        self.user_dao.update_user_password(user_id, new_password)

    def delete_user(self, user_id: int) -> None:
        """
        Löscht einen Benutzer
        """
        if not user_id or user_id <= 0:
            raise ValueError("Ungültige User-ID")

        existing_user = self.user_dao.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError("Benutzer existiert nicht")

        self.user_dao.delete_user(user_id)

    def validate_user_exists(self, user_id: int) -> bool:
        """
        Prüft ob ein Benutzer existiert
        """
        if not user_id or user_id <= 0:
            return False
        return self.user_dao.get_user_by_id(user_id) is not None

    def _validate_user_data(self, last_name: str, first_name: str, password: str, role: str) -> None:
        """
        Validiert Benutzerdaten nach Geschäftsregeln
        """
        if not last_name or not last_name.strip():
            raise ValueError("Nachname ist ein Pflichtfeld")
        if not first_name or not first_name.strip():
            raise ValueError("Vorname ist ein Pflichtfeld")
        if not password or len(password) < 4:
            raise ValueError("Passwort muss mindestens 4 Zeichen lang sein")
        if not role or not role.strip():
            raise ValueError("Rolle ist ein Pflichtfeld")
