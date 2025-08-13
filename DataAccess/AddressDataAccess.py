import os

from DataAccess.BaseDataAccess import BaseDataAccess
from Model.Address import Address


class AddressDataAccess(BaseDataAccess):
    def __init__(self, db_path: str = None):
        super().__init__(db_path)

    def get_address_by_id(self, address_id: int) -> Address | None:
        sql = """
        select AddressID, Street, Number, Zip, City, State, UserID
        from Address
        where addressID = ?    
        """
        row = self.fetchone(sql, (address_id,))
        if row:
            return Address(*row)
        return None


    def insert_address(self, street: str, number: str, zip: str, city: str, state: str, user_id) -> int:
        sql = """
        INSERT INTO address (Street, Number, Zip, City, State, UserID)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        new_id, _ = self.execute(sql, (street, number, zip, city, state, user_id))
        return Address(new_id, street, street, number, zip, city, state, user_id)


    def update_address(self, address: Address) -> None:
        sql = """
        UPDATE address
        SET street = ?, Number = ?, Zip = ?, City = ?, State = ?, UserID = ?
        WHERE addressID = ?
        """
        self.execute(sql, (address.street, address.number, address.zip, address.city, address.state, address.user_id))

    def delete_address(self, address_id: int) -> None:
        sql = "DELETE FROM address WHERE addressID = ?"
        self.execute(sql, (address_id,))

    def get_address_id(self, street: str, number: str, zip: str, city: str) -> int:
        sql ="""
        SELECT AddressID FROM address
        WHERE street = ? AND Number = ? AND Zip = ? AND City = ?"""
        address_id_tuple = self.fetchone(sql, (street, number, zip, city))
        return address_id_tuple[0] if address_id_tuple else None
        return address_id