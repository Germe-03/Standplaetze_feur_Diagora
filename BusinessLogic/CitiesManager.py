from typing import List, Optional, Dict

from DataAccess.CitiesDataAccess import CitiesDataAccess
from DataAccess.StateDataAccess import StateDataAccess
from Model.City import City


class CitiesManager:
    def __init__(self, db_path: str = None):
        self.cities_dao = CitiesDataAccess(db_path)
        self.state_dao = StateDataAccess(db_path)

    def create_city(self, name: str, state_id: int) -> City:
        """
        Erstellt eine neue Stadt mit Validierung der Geschäftsregeln
        """
        # Geschäftsregeln validieren
        self._validate_city_data(name, state_id)

        # Prüfen ob Kanton existiert
        state = self.state_dao.get_state_by_id(state_id)
        if not state:
            raise ValueError("Kanton existiert nicht")

        # Prüfen ob Stadt im selben Kanton bereits existiert
        existing_cities = self.cities_dao.get_city_by_name(name.strip())
        duplicate_city = next((c for c in existing_cities if c.state_id == state_id), None)
        if duplicate_city:
            raise ValueError("Diese Stadt existiert im Kanton bereits")

        # Stadt erstellen
        return self.cities_dao.insert_city(name.strip(), state_id)

    def get_city_by_id(self, city_id: int) -> Optional[City]:
        """
        Holt eine Stadt nach ID
        """
        if not city_id or city_id <= 0:
            raise ValueError("Ungültige Stadt-ID")

        return self.cities_dao.get_city_by_id(city_id)

    def get_cities_by_name(self, name: str) -> List[City]:
        """
        Holt alle Städte mit einem bestimmten Namen
        """
        if not name or not name.strip():
            raise ValueError("Stadtname muss angegeben werden")

        return self.cities_dao.get_city_by_name(name.strip())

    def get_cities_by_state(self, state_id: int) -> List[City]:
        """
        Holt alle Städte eines Bundeslands
        """
        if not state_id or state_id <= 0:
            raise ValueError("Ungültige State-ID")

        return self.cities_dao.get_cities_by_state_id(state_id)

    def get_all_cities(self) -> List[City]:
        """
        Holt alle Staedte
        """
        return self.cities_dao.get_all_cities()
    def update_city(self, city: City) -> None:
        """
        Aktualisiert eine bestehende Stadt
        """
        if not city or not city.city_id:
            raise ValueError("Ungültige Stadt")

        # Prüfen ob Stadt existiert
        existing_city = self.cities_dao.get_city_by_id(city.city_id)
        if not existing_city:
            raise ValueError("Stadt existiert nicht")

        # Geschäftsregeln validieren
        self._validate_city_data(city.name, city.state_id)

        # Prüfen ob Bundesland existiert
        state = self.state_dao.get_state_by_id(city.state_id)
        if not state:
            raise ValueError("Bundesland existiert nicht")

        # Prüfen ob Name im Bundesland schon von anderer Stadt belegt ist
        existing_cities = self.cities_dao.get_city_by_name(city.name.strip())
        duplicate_city = next(
            (
                c
                for c in existing_cities
                if c.city_id != city.city_id and c.state_id == city.state_id
            ),
            None,
        )
        if duplicate_city:
            raise ValueError("Eine andere Stadt mit gleichem Namen im Bundesland existiert bereits")

        # Stadt aktualisieren
        self.cities_dao.update_city(city)

    def delete_city(self, city_id: int) -> None:
        """
        Löscht eine Stadt
        """
        if not city_id or city_id <= 0:
            raise ValueError("Ungültige Stadt-ID")

        # Prüfen ob Stadt existiert
        existing_city = self.cities_dao.get_city_by_id(city_id)
        if not existing_city:
            raise ValueError("Stadt existiert nicht")

        # Stadt löschen
        self.cities_dao.delete_city(city_id)

    def validate_city_exists(self, city_id: int) -> bool:
        """
        Prüft ob eine Stadt existiert
        """
        if not city_id or city_id <= 0:
            return False

        city = self.cities_dao.get_city_by_id(city_id)
        return city is not None

    def get_city_statistics(self, state_id: int) -> Dict:
        """
        Gibt Statistiken über Städte in einem Bundesland zurück
        """
        if not state_id or state_id <= 0:
            raise ValueError("Ungültige State-ID")

        # Prüfen ob Bundesland existiert
        state = self.state_dao.get_state_by_id(state_id)
        if not state:
            raise ValueError("Bundesland existiert nicht")

        cities = self.get_cities_by_state(state_id)
        unique_names = {c.name for c in cities}

        return {
            "state_id": state_id,
            "state_name": state.name,
            "total_cities": len(cities),
            "unique_city_names": len(unique_names),
        }

    def _validate_city_data(self, name: str, state_id: int) -> None:
        """
        Validiert Stadtdaten nach Geschäftsregeln
        """
        # Pflichtfelder prüfen
        if not name or not name.strip():
            raise ValueError("Stadtname ist ein Pflichtfeld")

        if not state_id or state_id <= 0:
            raise ValueError("Bundesland ist ein Pflichtfeld")

        # Längenvalidierung
        if len(name.strip()) < 2:
            raise ValueError("Stadtname muss mindestens 2 Zeichen lang sein")

