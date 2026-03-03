from typing import List, Optional

from DataAccess.StateDataAccess import StateDataAccess
from Model.State import State


class StateManger:
    def __init__(self, db_path: str = None):
        self.state_dao = StateDataAccess(db_path)

    def create_state(self, name: str) -> State:
        """
        Erstellt ein neues Bundesland mit Validierung der Geschäftsregeln
        """
        self._validate_state_data(name)

        existing_state = self.state_dao.get_state_by_name(name.strip())
        if existing_state:
            raise ValueError("Dieses Bundesland existiert bereits")

        return self.state_dao.insert_state(name.strip())

    def get_state_by_id(self, state_id: int) -> Optional[State]:
        """
        Holt ein Bundesland nach ID
        """
        if not state_id or state_id <= 0:
            raise ValueError("Ungültige State-ID")
        return self.state_dao.get_state_by_id(state_id)

    def get_state_by_name(self, name: str) -> Optional[State]:
        """
        Holt ein Bundesland nach Namen
        """
        if not name or not name.strip():
            raise ValueError("Bundeslandname muss angegeben werden")
        return self.state_dao.get_state_by_name(name.strip())

    def get_all_states(self) -> List[State]:
        """
        Holt alle Bundesländer
        """
        return self.state_dao.get_all_states()

    def get_states_by_name_pattern(self, name_pattern: str) -> List[State]:
        """
        Holt Bundesländer anhand eines Namensmusters
        """
        if not name_pattern or not name_pattern.strip():
            raise ValueError("Namensmuster muss angegeben werden")
        return self.state_dao.get_states_by_name_pattern(name_pattern.strip())

    def update_state(self, state: State) -> None:
        """
        Aktualisiert ein bestehendes Bundesland
        """
        if not state or not state.state_id:
            raise ValueError("Ungültiges Bundesland")

        existing_state = self.state_dao.get_state_by_id(state.state_id)
        if not existing_state:
            raise ValueError("Bundesland existiert nicht")

        self._validate_state_data(state.name)
        self.state_dao.update_state(state)

    def delete_state(self, state_id: int) -> None:
        """
        Löscht ein Bundesland
        """
        if not state_id or state_id <= 0:
            raise ValueError("Ungültige State-ID")

        existing_state = self.state_dao.get_state_by_id(state_id)
        if not existing_state:
            raise ValueError("Bundesland existiert nicht")

        self.state_dao.delete_state(state_id)

    def validate_state_exists(self, state_id: int) -> bool:
        """
        Prüft ob ein Bundesland existiert
        """
        if not state_id or state_id <= 0:
            return False
        return self.state_dao.get_state_by_id(state_id) is not None

    def _validate_state_data(self, name: str) -> None:
        """
        Validiert Bundesland-Daten nach Geschäftsregeln
        """
        if not name or not name.strip():
            raise ValueError("Bundeslandname ist ein Pflichtfeld")
        if len(name.strip()) < 2:
            raise ValueError("Bundeslandname muss mindestens 2 Zeichen lang sein")
