from DataAccess.BaseDataAccess import BaseDataAccess
from Model.State import State


class StateDataAccess(BaseDataAccess):
    def __init__(self, db_path: str = None):
        super().__init__(db_path)

    def get_state_by_id(self, state_id: int) -> State | None:
        sql = """
        select StateID, Name
        from States
        where StateID = ?   
        """
        row = self.fetchone(sql, (state_id,))
        if row:
            return State(*row)
        return None

    def get_state_by_name(self, name: str) -> State | None:
        sql = """
        select StateID, Name
        from States
        where Name = ?
        """
        row = self.fetchone(sql, (name,))
        if row:
            return State(*row)
        return None

    def get_all_states(self) -> list[State]:
        sql = """
        select StateID, Name
        from States
        order by Name
        """
        rows = self.fetchall(sql)
        return [State(*row) for row in rows]

    def get_states_by_name_pattern(self, name_pattern: str) -> list[State]:
        sql = """
        select StateID, Name
        from States
        where Name LIKE ?
        order by Name
        """
        rows = self.fetchall(sql, (f"%{name_pattern}%",))
        return [State(*row) for row in rows]

    def insert_state(self, name: str) -> State:
        sql = """
        INSERT INTO States (Name)
        VALUES (?)
        """
        new_id, _ = self.execute(sql, (name,))
        return State(new_id, name)

    def update_state(self, state: State) -> None:
        sql = """
        UPDATE States
        SET Name = ?
        WHERE StateID = ?
        """
        self.execute(sql, (state.name, state.state_id))

    def delete_state(self, state_id: int) -> None:
        sql = "DELETE FROM States WHERE StateID = ?"
        self.execute(sql, (state_id,))
