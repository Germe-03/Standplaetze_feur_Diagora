from DataAccess.BookingDataAccess import BookingDataAccess
from DataAccess.LocationsDataAccess import LocationsDataAccess
from DataAccess.CampaignDataAccess import CampaignDataAccess
from DataAccess.UserDataAccess import UserDataAccess
from Model.Booking import Booking
from Model.Location import Location
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict


class BookingManager:
    def __init__(self, db_path: str = None):
        self.booking_dao = BookingDataAccess(db_path)
        self.location_dao = LocationsDataAccess(db_path)
        self.campaign_dao = CampaignDataAccess(db_path)
        self.user_dao = UserDataAccess(db_path)

    def create_booking(self, date_of_event: date, price: float, confirmed: bool, 
                      location_id: int, cancelled: bool, campaign_id: int, user_id: int) -> Booking:
        """
        Erstellt eine neue Buchung mit Validierung der Geschäftsregeln
        """
        # Geschäftsregeln validieren
        self._validate_booking_data(date_of_event, price, location_id, campaign_id, user_id)
        
        # Prüfen ob Location existiert
        location = self.location_dao.get_location_by_id(location_id)
        if not location:
            raise ValueError("Standort existiert nicht")
        
        # Prüfen ob Campaign existiert
        campaign = self.campaign_dao.get_campaign_by_id(campaign_id)
        if not campaign:
            raise ValueError("Kampagne existiert nicht")
        
        # Prüfen ob User existiert
        user = self.user_dao.get_user_by_id(user_id)
        if not user:
            raise ValueError("Benutzer existiert nicht")
        
        # Prüfen ob Standort verfügbar ist
        if not self._is_location_available(location_id, date_of_event):
            raise ValueError("Standort ist an diesem Datum nicht verfügbar")
        
        # Prüfen ob Preis im erlaubten Bereich liegt
        if not self._is_price_valid(price, location):
            raise ValueError("Preis liegt außerhalb des erlaubten Bereichs")
        
        # Buchung erstellen
        return self.booking_dao.insert_booking(date_of_event, price, confirmed, location_id, cancelled, campaign_id, user_id)

    def get_booking_by_id(self, booking_id: int) -> Optional[Booking]:
        """
        Holt eine Buchung nach ID
        """
        if not booking_id or booking_id <= 0:
            raise ValueError("Ungültige Buchungs-ID")
        
        return self.booking_dao.get_booking_by_id(booking_id)

    def get_bookings_by_user(self, user_id: int) -> List[Booking]:
        """
        Holt alle Buchungen eines Benutzers
        """
        if not user_id or user_id <= 0:
            raise ValueError("Ungültige User-ID")
        
        return self.booking_dao.get_bookings_by_user_id(user_id)

    def get_all_bookings(self) -> List[Booking]:
        """
        Holt alle Buchungen
        """
        return self.booking_dao.get_all_bookings()

    def get_next_booking_id(self) -> int:
        """
        Liefert die naechste Booking-ID fuer die UI
        """
        return self.booking_dao.get_next_id("Bookings", "BookingID")

    def update_booking_fields(
        self,
        booking_id: int,
        date_of_event: date,
        price: float,
        confirmed: bool,
        location_id: int,
        cancelled: bool,
        campaign_id: int,
        user_id: int,
    ) -> None:
        """
        Aktualisiert Buchungsfelder anhand der Booking-ID
        """
        if not booking_id or booking_id <= 0:
            raise ValueError("Ungueltige Buchungs-ID")
        self.booking_dao.update_booking_fields(
            booking_id=booking_id,
            date_of_event=date_of_event,
            price=price,
            confirmed=confirmed,
            location_id=location_id,
            cancelled=cancelled,
            campaign_id=campaign_id,
            user_id=user_id,
        )

    def get_bookings_by_location(self, location_id: int) -> List[Booking]:
        """
        Holt alle Buchungen für einen Standort
        """
        if not location_id or location_id <= 0:
            raise ValueError("Ungültige Location-ID")
        
        return self.booking_dao.get_bookings_by_location_id(location_id)

    def get_bookings_by_campaign(self, campaign_id: int) -> List[Booking]:
        """
        Holt alle Buchungen für eine Kampagne
        """
        if not campaign_id or campaign_id <= 0:
            raise ValueError("Ungültige Campaign-ID")
        
        return self.booking_dao.get_bookings_by_campaign_id(campaign_id)

    def get_bookings_by_date_range(self, start_date: date, end_date: date) -> List[Booking]:
        """
        Holt alle Buchungen in einem Datumsbereich
        """
        if not start_date or not end_date:
            raise ValueError("Start- und Enddatum müssen angegeben werden")
        
        if start_date > end_date:
            raise ValueError("Startdatum muss vor dem Enddatum liegen")
        
        return self.booking_dao.get_bookings_by_date_of_event(start_date.isoformat(), end_date.isoformat())

    def get_bookings_by_price_range(self, min_price: float, max_price: float) -> List[Booking]:
        """
        Holt alle Buchungen in einem Preissegment
        """
        if min_price < 0 or max_price < 0:
            raise ValueError("Preise dürfen nicht negativ sein")
        
        if min_price > max_price:
            raise ValueError("Minimalpreis muss kleiner als Maximalpreis sein")
        
        return self.booking_dao.get_bookings_by_price(min_price, max_price)

    def get_bookings_by_city(self, city_name: str) -> List[Booking]:
        """
        Holt alle Buchungen in einer bestimmten Stadt
        """
        if not city_name or not city_name.strip():
            raise ValueError("Stadtname muss angegeben werden")
        
        return self.booking_dao.get_bookings_by_city(city_name.strip())

    def get_bookings_by_state(self, state_name: str) -> List[Booking]:
        """
        Holt alle Buchungen in einem bestimmten Bundesland
        """
        if not state_name or not state_name.strip():
            raise ValueError("Bundeslandname muss angegeben werden")
        
        return self.booking_dao.get_bookings_by_state(state_name.strip())

    def update_booking(self, booking: Booking) -> None:
        """
        Aktualisiert eine bestehende Buchung
        """
        if not booking or not booking.booking_id:
            raise ValueError("Ungültige Buchung")
        
        # Prüfen ob Buchung existiert
        existing_booking = self.booking_dao.get_booking_by_id(booking.booking_id)
        if not existing_booking:
            raise ValueError("Buchung existiert nicht")
        
        # Geschäftsregeln validieren
        self._validate_booking_data(
            booking.date_of_event, booking.price, booking.location_id, 
            booking.campaign_id, booking.user_id
        )
        
        # Prüfen ob Standort verfügbar ist (falls Datum geändert wurde)
        if booking.date_of_event != existing_booking.date_of_event:
            if not self._is_location_available(booking.location_id, booking.date_of_event, exclude_booking_id=booking.booking_id):
                raise ValueError("Standort ist an diesem Datum nicht verfügbar")
        
        # Buchung aktualisieren
        self.booking_dao.update_booking(booking)

    def confirm_booking(self, booking_id: int) -> None:
        """
        Bestätigt eine Buchung
        """
        if not booking_id or booking_id <= 0:
            raise ValueError("Ungültige Buchungs-ID")
        
        booking = self.booking_dao.get_booking_by_id(booking_id)
        if not booking:
            raise ValueError("Buchung existiert nicht")
        
        if booking.confirmed:
            raise ValueError("Buchung ist bereits bestätigt")
        
        if booking.cancelled:
            raise ValueError("Stornierte Buchungen können nicht bestätigt werden")
        
        # Buchung bestätigen
        booking.confirmed = True
        self.booking_dao.update_booking(booking)

    def cancel_booking(self, booking_id: int) -> None:
        """
        Storniert eine Buchung
        """
        if not booking_id or booking_id <= 0:
            raise ValueError("Ungültige Buchungs-ID")
        
        booking = self.booking_dao.get_booking_by_id(booking_id)
        if not booking:
            raise ValueError("Buchung existiert nicht")
        
        if booking.cancelled:
            raise ValueError("Buchung ist bereits storniert")
        
        # Prüfen ob Stornierung noch möglich ist (z.B. 24h vor Event)
        if self._is_cancellation_allowed(booking.date_of_event):
            booking.cancelled = True
            self.booking_dao.update_booking(booking)
        else:
            raise ValueError("Stornierung ist nicht mehr möglich (zu kurzfristig)")

    def delete_booking(self, booking_id: int) -> None:
        """
        Löscht eine Buchung
        """
        if not booking_id or booking_id <= 0:
            raise ValueError("Ungültige Buchungs-ID")
        
        # Prüfen ob Buchung existiert
        existing_booking = self.booking_dao.get_booking_by_id(booking_id)
        if not existing_booking:
            raise ValueError("Buchung existiert nicht")
        
        # Prüfen ob Buchung gelöscht werden darf
        if existing_booking.confirmed and not existing_booking.cancelled:
            raise ValueError("Bestätigte Buchungen können nicht gelöscht werden")
        
        # Buchung löschen
        self.booking_dao.delete_booking(booking_id)

    def get_booking_statistics(self, start_date: date = None, end_date: date = None) -> Dict:
        """
        Gibt Statistiken über Buchungen zurück
        """
        if start_date and end_date:
            bookings = self.get_bookings_by_date_range(start_date, end_date)
        else:
            # Alle Buchungen der letzten 30 Tage
            end_date = date.today()
            start_date = date(end_date.year, end_date.month, max(1, end_date.day - 30))
            bookings = self.get_bookings_by_date_range(start_date, end_date)
        
        if not bookings:
            return {
                "total_bookings": 0,
                "confirmed_bookings": 0,
                "cancelled_bookings": 0,
                "total_revenue": 0.0,
                "average_price": 0.0
            }
        
        confirmed_count = sum(1 for b in bookings if b.confirmed and not b.cancelled)
        cancelled_count = sum(1 for b in bookings if b.cancelled)
        total_revenue = sum(b.price for b in bookings if b.confirmed and not b.cancelled)
        average_price = total_revenue / confirmed_count if confirmed_count > 0 else 0.0
        
        return {
            "total_bookings": len(bookings),
            "confirmed_bookings": confirmed_count,
            "cancelled_bookings": cancelled_count,
            "total_revenue": round(total_revenue, 2),
            "average_price": round(average_price, 2)
        }

    def _validate_booking_data(self, date_of_event: date, price: float, location_id: int, 
                              campaign_id: int, user_id: int) -> None:
        """
        Validiert Buchungsdaten nach Geschäftsregeln
        """
        # Datum validieren
        if not date_of_event:
            raise ValueError("Eventdatum ist ein Pflichtfeld")
        
        if date_of_event < date.today():
            raise ValueError("Eventdatum darf nicht in der Vergangenheit liegen")
        
        # Preis validieren
        if price is not None and price < 0:
            raise ValueError("Preis darf nicht negativ sein")
        
        # IDs validieren
        if not location_id or location_id <= 0:
            raise ValueError("Standort ist ein Pflichtfeld")
        
        if not campaign_id or campaign_id <= 0:
            raise ValueError("Kampagne ist ein Pflichtfeld")
        
        if not user_id or user_id <= 0:
            raise ValueError("Benutzer ist ein Pflichtfeld")

    def _is_location_available(self, location_id: int, event_date: date, exclude_booking_id: int = None) -> bool:
        """
        Prüft ob ein Standort an einem bestimmten Datum verfügbar ist
        """
        # Alle Buchungen für diesen Standort an diesem Datum
        location_bookings = self.booking_dao.get_bookings_by_location_id(location_id)
        
        # Buchungen am Eventdatum filtern
        conflicting_bookings = [
            b for b in location_bookings 
            if b.date_of_event == event_date and not b.cancelled
        ]
        
        # Aktuelle Buchung ausschließen (bei Updates)
        if exclude_booking_id:
            conflicting_bookings = [b for b in conflicting_bookings if b.booking_id != exclude_booking_id]
        
        # Standort ist verfügbar wenn keine Konflikte
        return len(conflicting_bookings) == 0

    def _is_price_valid(self, price: float, location: Location) -> bool:
        """
        Prüft ob der Preis im erlaubten Bereich liegt
        """
        if price is None:
            return True  # Preis ist optional
        
        if location.price is None:
            return True  # Keine Preisbeschränkung am Standort
        
        # Preis sollte nicht mehr als 50% über dem Standortpreis liegen
        max_allowed_price = location.price * 1.5
        return price <= max_allowed_price

    def _is_cancellation_allowed(self, event_date: date) -> bool:
        """
        Prüft ob eine Stornierung noch möglich ist
        """
        # Stornierung bis 24h vor Event möglich
        cancellation_deadline = event_date - timedelta(days=1)
        return date.today() <= cancellation_deadline


