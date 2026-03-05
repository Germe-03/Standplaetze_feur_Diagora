from DataAccess.BaseDataAccess import BaseDataAccess
from Model.User import User


class UserDataAccess(BaseDataAccess):
    def __init__(self, db_path: str = None):
        super().__init__(db_path)
        self._ensure_is_active_column()
        self._normalize_role_values()

    def _ensure_is_active_column(self) -> None:
        rows = self.fetchall("PRAGMA table_info(Users)")
        columns = {str(row[1]).lower() for row in rows}
        if "isactive" in columns:
            return
        self.execute("ALTER TABLE Users ADD COLUMN IsActive INTEGER NOT NULL DEFAULT 1")
        self.execute("UPDATE Users SET IsActive = 1 WHERE IsActive IS NULL")

    def _next_free_user_id(self) -> int:
        rows = self.fetchall("SELECT UserID FROM Users ORDER BY UserID")
        next_id = 1
        for row in rows:
            current = int(row[0])
            if current != next_id:
                return next_id
            next_id += 1
        return next_id

    def _normalize_role_values(self) -> None:
        self.execute("UPDATE Users SET Role = 'Admin' WHERE lower(trim(Role)) = 'admin'")
        self.execute("UPDATE Users SET Role = 'User' WHERE lower(trim(Role)) = 'user'")
        self.execute("UPDATE Users SET Role = 'Viewer' WHERE lower(trim(Role)) = 'viewer'")

    def get_user_by_id(self, user_id: int) -> User | None:
        sql = """
        select UserID, LastName, FirstName, Password, Role, IsActive
        from Users
        where UserID = ?   
        """
        row = self.fetchone(sql, (user_id,))
        if row:
            return User(*row)
        return None

    def get_user_by_name(self, first_name: str, last_name: str) -> list[User]:
        sql = """
        select UserID, LastName, FirstName, Password, Role, IsActive
        from Users
        where FirstName = ? AND LastName = ?
        """
        rows = self.fetchall(sql, (first_name, last_name))
        return [User(*row) for row in rows]

    def get_users_by_first_name(self, first_name: str) -> list[User]:
        sql = """
        select UserID, LastName, FirstName, Password, Role, IsActive
        from Users
        where FirstName = ?
        """
        rows = self.fetchall(sql, (first_name,))
        return [User(*row) for row in rows]

    def get_users_by_last_name(self, last_name: str) -> list[User]:
        sql = """
        select UserID, LastName, FirstName, Password, Role, IsActive
        from Users
        where LastName = ?
        """
        rows = self.fetchall(sql, (last_name,))
        return [User(*row) for row in rows]

    def get_users_by_role(self, role: str) -> list[User]:
        sql = """
        select UserID, LastName, FirstName, Password, Role, IsActive
        from Users
        where Role = ?
        """
        rows = self.fetchall(sql, (role,))
        return [User(*row) for row in rows]

    def get_users_by_name_pattern(self, name_pattern: str) -> list[User]:
        sql = """
        select UserID, LastName, FirstName, Password, Role, IsActive
        from Users
        where FirstName LIKE ? OR LastName LIKE ?
        order by LastName, FirstName
        """
        pattern = f"%{name_pattern}%"
        rows = self.fetchall(sql, (pattern, pattern))
        return [User(*row) for row in rows]

    def get_all_users(self) -> list[User]:
        sql = """
        select UserID, LastName, FirstName, Password, Role, IsActive
        from Users
        order by LastName, FirstName
        """
        rows = self.fetchall(sql)
        return [User(*row) for row in rows]

    def authenticate_user(self, first_name: str, last_name: str, password: str) -> User | None:
        sql = """
        select UserID, LastName, FirstName, Password, Role, IsActive
        from Users
        where FirstName = ? AND LastName = ? AND Password = ?
        """
        row = self.fetchone(sql, (first_name, last_name, password))
        if row:
            return User(*row)
        return None

    def insert_user(self, last_name: str, first_name: str, password: str, role: str, is_active: bool = True) -> User:
        new_id = self._next_free_user_id()
        sql = """
        INSERT INTO Users (UserID, LastName, FirstName, Password, Role, IsActive)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        self.execute(sql, (new_id, last_name, first_name, password, role, 1 if is_active else 0))
        return User(new_id, last_name, first_name, password, role, is_active)

    def update_user(self, user: User) -> None:
        sql = """
        UPDATE Users
        SET LastName = ?, FirstName = ?, Password = ?, Role = ?, IsActive = ?
        WHERE UserID = ?
        """
        self.execute(sql, (user.last_name, user.first_name, user.password, user.role, 1 if user.is_active else 0, user.user_id))

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
