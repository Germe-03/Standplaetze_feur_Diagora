from DataAccess.AddressDataAccess import AddressDataAccess
from Model.Address import Address
from typing import List, Optional


class AddressManager:
    def __init__(self, db_path: str = None):
        self.address_dao = AddressDataAccess(db_path)

    def create_address(self, street: str, number: str, zip_code: str, city: str, state_id: int, user_id: int) -> Address:
        """
        Erstellt eine neue Adresse mit Validierung der Geschäftsregeln
        """
        # Geschäftsregeln validieren
        self._validate_address_data(street, number, zip_code, city, state_id, user_id)
        
        # Prüfen ob Adresse bereits existiert
        existing_address = self.address_dao.get_address_id(street, number, zip_code, city)
        if existing_address:
            raise ValueError("Diese Adresse existiert bereits")
        
        # Adresse erstellen
        return self.address_dao.insert_address(street, number, zip_code, city, state_id, user_id)

    def get_address_by_id(self, address_id: int) -> Optional[Address]:
        """
        Holt eine Adresse nach ID
        """
        if not address_id or address_id <= 0:
            raise ValueError("Ungültige Adress-ID")
        
        return self.address_dao.get_address_by_id(address_id)

    def get_addresses_by_user(self, user_id: int) -> List[Address]:
        """
        Holt alle Adressen eines Benutzers
        """
        if not user_id or user_id <= 0:
            raise ValueError("Ungültige User-ID")
        
        return self.address_dao.get_addresses_by_user_id(user_id)

    def search_addresses(self, street: str = None, city: str = None, zip_code: str = None) -> List[Address]:
        """
        Sucht Adressen nach verschiedenen Kriterien
        """
        addresses = []
        
        if street:
            # Suche nach Straße
            street_addresses = self.address_dao.get_addresses_by_street(street)
            addresses.extend(street_addresses)
        
        if city:
            # Suche nach Stadt
            city_addresses = self.address_dao.get_addresses_by_city(city)
            addresses.extend(city_addresses)
        
        if zip_code:
            # Suche nach PLZ
            zip_addresses = self.address_dao.get_addresses_by_zip(zip_code)
            addresses.extend(zip_addresses)
        
        # Duplikate entfernen und nach Straße sortieren
        unique_addresses = list({addr.address_id: addr for addr in addresses}.values())
        return sorted(unique_addresses, key=lambda x: x.street)

    def update_address(self, address: Address) -> None:
        """
        Aktualisiert eine bestehende Adresse
        """
        if not address or not address.address_id:
            raise ValueError("Ungültige Adresse")
        
        # Geschäftsregeln validieren
        self._validate_address_data(
            address.street, address.number, address.zip, 
            address.city, address.state_id, address.user_id
        )
        
        # Prüfen ob Adresse existiert
        existing_address = self.address_dao.get_address_by_id(address.address_id)
        if not existing_address:
            raise ValueError("Adresse existiert nicht")
        
        # Adresse aktualisieren
        self.address_dao.update_address(address)

    def delete_address(self, address_id: int) -> None:
        """
        Löscht eine Adresse
        """
        if not address_id or address_id <= 0:
            raise ValueError("Ungültige Adress-ID")
        
        # Prüfen ob Adresse existiert
        existing_address = self.address_dao.get_address_by_id(address_id)
        if not existing_address:
            raise ValueError("Adresse existiert nicht")
        
        # Prüfen ob Adresse noch von anderen Entitäten referenziert wird
        # (z.B. von Locations oder Users)
        # TODO: Implementiere Referenzprüfung
        
        # Adresse löschen
        self.address_dao.delete_address(address_id)

    def get_address_id(self, street: str, number: str, zip_code: str, city: str) -> Optional[int]:
        """
        Holt die Adress-ID für eine spezifische Adresse
        """
        if not all([street, number, zip_code, city]):
            raise ValueError("Alle Adressfelder müssen ausgefüllt sein")
        
        return self.address_dao.get_address_id(street, number, zip_code, city)

    def validate_address_exists(self, address_id: int) -> bool:
        """
        Prüft ob eine Adresse existiert
        """
        if not address_id or address_id <= 0:
            return False
        
        address = self.address_dao.get_address_by_id(address_id)
        return address is not None

    def get_addresses_by_state(self, state_id: int) -> List[Address]:
        """
        Holt alle Adressen in einem bestimmten Bundesland
        """
        if not state_id or state_id <= 0:
            raise ValueError("Ungültige State-ID")
        
        return self.address_dao.get_addresses_by_state_id(state_id)

    def _validate_address_data(self, street: str, number: str, zip_code: str, city: str, state_id: int, user_id: int) -> None:
        """
        Validiert Adressdaten nach Geschäftsregeln
        """
        # Pflichtfelder prüfen
        if not street or not street.strip():
            raise ValueError("Straße ist ein Pflichtfeld")
        
        if not number or not number.strip():
            raise ValueError("Hausnummer ist ein Pflichtfeld")
        
        if not zip_code or not zip_code.strip():
            raise ValueError("PLZ ist ein Pflichtfeld")
        
        if not city or not city.strip():
            raise ValueError("Stadt ist ein Pflichtfeld")
        
        if not state_id or state_id <= 0:
            raise ValueError("Bundesland ist ein Pflichtfeld")
        
        if not user_id or user_id <= 0:
            raise ValueError("Benutzer ist ein Pflichtfeld")
        
        # Längenvalidierung
        if len(street.strip()) < 2:
            raise ValueError("Straßenname muss mindestens 2 Zeichen lang sein")
        
        if len(city.strip()) < 2:
            raise ValueError("Stadtname muss mindestens 2 Zeichen lang sein")
        
        if len(zip_code.strip()) < 4:
            raise ValueError("PLZ muss mindestens 4 Zeichen lang sein")
        
        # Formatvalidierung für PLZ (nur Zahlen)
        if not zip_code.strip().isdigit():
            raise ValueError("PLZ darf nur Zahlen enthalten")
