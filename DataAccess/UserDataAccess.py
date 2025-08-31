from DataAccess.BaseDataAccess import BaseDataAccess
from Model.User import User


class UserDataAccess(BaseDataAccess):
    def __init__(self, db_path: str = None):
        super().__init__(db_path)

    def get_user_by_id(self, user_id: int) -> User | None:
        sql = """
        select UserID, LastName, FirstName, Password, Role
        from Users
        where UserID = ?   
        """
        row = self.fetchone(sql, (user_id,))
        if row:
            return User(*row)
        return None

    def get_user_by_name(self, first_name: str, last_name: str) -> list[User]:
        sql = """
        select UserID, LastName, FirstName, Password, Role
        from Users
        where FirstName = ? AND LastName = ?
        """
        rows = self.fetchall(sql, (first_name, last_name))
        return [User(*row) for row in rows]

    def get_users_by_first_name(self, first_name: str) -> list[User]:
        sql = """
        select UserID, LastName, FirstName, Password, Role
        from Users
        where FirstName = ?
        """
        rows = self.fetchall(sql, (first_name,))
        return [User(*row) for row in rows]

    def get_users_by_last_name(self, last_name: str) -> list[User]:
        sql = """
        select UserID, LastName, FirstName, Password, Role
        from Users
        where LastName = ?
        """
        rows = self.fetchall(sql, (last_name,))
        return [User(*row) for row in rows]

    def get_users_by_role(self, role: str) -> list[User]:
        sql = """
        select UserID, LastName, FirstName, Password, Role
        from Users
        where Role = ?
        """
        rows = self.fetchall(sql, (role,))
        return [User(*row) for row in rows]

    def get_users_by_name_pattern(self, name_pattern: str) -> list[User]:
        sql = """
        select UserID, LastName, FirstName, Password, Role
        from Users
        where FirstName LIKE ? OR LastName LIKE ?
        order by LastName, FirstName
        """
        pattern = f"%{name_pattern}%"
        rows = self.fetchall(sql, (pattern, pattern))
        return [User(*row) for row in rows]

    def get_all_users(self) -> list[User]:
        sql = """
        select UserID, LastName, FirstName, Password, Role
        from Users
        order by LastName, FirstName
        """
        rows = self.fetchall(sql)
        return [User(*row) for row in rows]

    def authenticate_user(self, first_name: str, last_name: str, password: str) -> User | None:
        sql = """
        select UserID, LastName, FirstName, Password, Role
        from Users
        where FirstName = ? AND LastName = ? AND Password = ?
        """
        row = self.fetchone(sql, (first_name, last_name, password))
        if row:
            return User(*row)
        return None

    def insert_user(self, last_name: str, first_name: str, password: str, role: str) -> User:
        sql = """
        INSERT INTO Users (LastName, FirstName, Password, Role)
        VALUES (?, ?, ?, ?)
        """
        new_id, _ = self.execute(sql, (last_name, first_name, password, role))
        return User(new_id, last_name, first_name, password, role)

    def update_user(self, user: User) -> None:
        sql = """
        UPDATE Users
        SET LastName = ?, FirstName = ?, Password = ?, Role = ?
        WHERE UserID = ?
        """
        self.execute(sql, (user.last_name, user.first_name, user.password, user.role, user.user_id))

    def update_user_password(self, user_id: int, new_password: str) -> None:
        sql = """
        UPDATE Users
        SET Password = ?
        WHERE UserID = ?
        """
        self.execute(sql, (new_password, user_id))

    def delete_user(self, user_id: int) -> None:
        sql = "DELETE FROM Users WHERE UserID = ?"
        self.execute(sql, (user_id,))
