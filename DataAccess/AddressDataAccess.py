from DataAccess.BaseDataAccess import BaseDataAccess
from Model.Address import Address


class AddressDataAccess(BaseDataAccess):
    def __init__(self, db_path: str = None):
        super().__init__(db_path)

    def get_address_by_id(self, address_id: int) -> Address | None:
        sql = """
        select AddressID, Street, Number, Zip, City, StateID, UserID
        from Address
        where AddressID = ?    
        """
        row = self.fetchone(sql, (address_id,))
        if row:
            return Address(*row)
        return None

    def get_addresses_by_user_id(self, user_id: int) -> list[Address]:
        sql = """
        select AddressID, Street, Number, Zip, City, StateID, UserID
        from Address
        where UserID = ?
        """
        rows = self.fetchall(sql, (user_id,))
        return [Address(*row) for row in rows]

    def get_addresses_by_street(self, street: str) -> list[Address]:
        sql = """
        select AddressID, Street, Number, Zip, City, StateID, UserID
        from Address
        where Street = ?
        """
        rows = self.fetchall(sql, (street,))
        return [Address(*row) for row in rows]

    def get_addresses_by_city(self, city: str) -> list[Address]:
        sql = """
        select AddressID, Street, Number, Zip, City, StateID, UserID
        from Address
        where City = ?
        """
        rows = self.fetchall(sql, (city,))
        return [Address(*row) for row in rows]

    def get_addresses_by_zip(self, zip_code: str) -> list[Address]:
        sql = """
        select AddressID, Street, Number, Zip, City, StateID, UserID
        from Address
        where Zip = ?
        """
        rows = self.fetchall(sql, (zip_code,))
        return [Address(*row) for row in rows]

    def get_addresses_by_state_id(self, state_id: int) -> list[Address]:
        sql = """
        select AddressID, Street, Number, Zip, City, StateID, UserID
        from Address
        where StateID = ?
        """
        rows = self.fetchall(sql, (state_id,))
        return [Address(*row) for row in rows]


    def insert_address(self, street: str, number: str, zip: str, city: str, state_id: int, user_id: int) -> Address:
        sql = """
        INSERT INTO address (Street, Number, Zip, City, StateID, UserID)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        new_id, _ = self.execute(sql, (street, number, zip, city, state_id, user_id))
        return Address(new_id, street, number, zip, city, state_id, user_id)


    def update_address(self, address: Address) -> None:
        sql = """
        UPDATE address
        SET street = ?, Number = ?, Zip = ?, City = ?, StateID = ?, UserID = ?
        WHERE addressID = ?
        """
        self.execute(
            sql,
            (
                address.street,
                address.number,
                address.zip,
                address.city,
                address.state_id,
                address.user_id,
                address.address_id,
            ),
        )

    def delete_address(self, address_id: int) -> None:
        sql = "DELETE FROM address WHERE addressID = ?"
        self.execute(sql, (address_id,))

    def get_address_id(self, street: str, number: str, zip: str, city: str) -> int:
        sql ="""
        SELECT AddressID FROM address
        WHERE street = ? AND Number = ? AND Zip = ? AND City = ?"""
        address_id_tuple = self.fetchone(sql, (street, number, zip, city))
        return address_id_tuple[0] if address_id_tuple else None
