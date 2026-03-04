from datetime import date, datetime

from BusinessLogic.BookingManager import BookingManager
from BusinessLogic.CampaignManager import CampaignManager
from BusinessLogic.CitiesManager import CitiesManager
from BusinessLogic.CityLimitManager import CityLimitManager
from BusinessLogic.LocationsLimitManager import LocationsLimitManager
from BusinessLogic.LocationsManager import LocationsManager
from BusinessLogic.StateManager import StateManager
from BusinessLogic.UserManager import UserManager


class WebAppManager:
    def __init__(self, db_path: str):
        self.booking_manager = BookingManager(db_path)
        self.campaign_manager = CampaignManager(db_path)
        self.cities_manager = CitiesManager(db_path)
        self.city_limit_manager = CityLimitManager(db_path)
        self.location_limit_manager = LocationsLimitManager(db_path)
        self.locations_manager = LocationsManager(db_path)
        self.state_manager = StateManager(db_path)
        self.user_manager = UserManager(db_path)

    @staticmethod
    def _to_bool(value, default: bool = False) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return default
        return str(value).strip().lower() in {"1", "true", "yes", "ja", "on"}

    @staticmethod
    def _to_date(value) -> date:
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        return date.fromisoformat(str(value))

    @staticmethod
    def _to_optional_int(value):
        if value in (None, ""):
            return None
        return int(value)

    def _resolve_city_id(self, payload: dict) -> int:
        city_id_raw = payload.get("city_id")
        city_name = str(payload.get("city_name") or "").strip()
        kanton_name = str(payload.get("kanton_name") or "").strip()

        if city_id_raw not in (None, ""):
            return int(city_id_raw)

        if not city_name:
            raise ValueError("Missing fields: city_name")

        cities = self.cities_manager.get_cities_by_name(city_name)
        existing_city = None
        for city in cities:
            if city.name.strip().lower() == city_name.lower():
                existing_city = city
                break

        if existing_city:
            return existing_city.city_id

        if not kanton_name:
            raise ValueError("Fuer neue Staedte ist ein Kanton erforderlich.")

        state = self.state_manager.get_state_by_name(kanton_name)
        if not state:
            state = self.state_manager.create_state(kanton_name)

        new_city = self.cities_manager.create_city(city_name, state.state_id)
        return new_city.city_id

    def _upsert_location_limits(
        self,
        location_id: int,
        user_id: int,
        limit_yearly: int | None,
        limit_monthly: int | None,
        limit_campaign: int | None,
        valid_from: date | None = None,
    ) -> None:
        if limit_yearly is None and limit_monthly is None and limit_campaign is None:
            return

        effective_valid_from = valid_from or date.today()
        self.location_limit_manager.upsert_location_limit(
            location_id=location_id,
            valid_from=effective_valid_from,
            user_id=user_id,
            location_limit_yearly=limit_yearly,
            location_limit_monthly=limit_monthly,
            location_limit_campaign=limit_campaign,
        )

    def _booking_to_dict(self, booking) -> dict:
        location = self.locations_manager.get_location_by_id(booking.location_id)
        campaign = self.campaign_manager.get_campaign_by_id(booking.campaign_id)
        city_name = None
        if location:
            city = self.cities_manager.get_city_by_id(location.city_id)
            city_name = city.name if city else None
        created_at = self._to_date(booking.date_of_booking)
        event_date = self._to_date(booking.date_of_event)
        return {
            "id": booking.booking_id,
            "created_at": str(created_at),
            "date": str(event_date),
            "location_id": booking.location_id,
            "campaign_id": booking.campaign_id,
            "user_id": booking.user_id,
            "stand": location.name if location else f"Location {booking.location_id}",
            "city": city_name or "-",
            "campaign": campaign.name if campaign else f"Campaign {booking.campaign_id}",
            "price": float(booking.price) if booking.price is not None else 0.0,
            "confirmed": bool(booking.confirmed),
            "cancelled": bool(booking.cancelled),
        }

    def get_dashboard(self, month_param: str | None = None) -> dict:
        today = date.today()
        selected_year = today.year
        selected_month = None

        if month_param:
            try:
                y_str, m_str = str(month_param).split("-")
                year = int(y_str)
                month = int(m_str)
                if 1 <= month <= 12:
                    selected_year = year
                    selected_month = month
            except (ValueError, TypeError):
                pass

        bookings = self.booking_manager.get_all_bookings()

        scoped = []
        for booking in bookings:
            if bool(booking.cancelled):
                continue
            event_date = self._to_date(booking.date_of_event)
            if event_date.year != selected_year:
                continue
            if selected_month is not None and event_date.month != selected_month:
                continue
            scoped.append(booking)

        total = len(scoped)
        confirmed = sum(1 for b in scoped if bool(b.confirmed))
        open_bookings = sum(1 for b in scoped if not bool(b.confirmed))
        revenue = sum(float(b.price or 0.0) for b in scoped)
        return {
            "total": total,
            "confirmed": confirmed,
            "open": open_bookings,
            "revenue": round(revenue, 2),
            "year": selected_year,
            "month": selected_month,
        }

    def get_bookings(self) -> list[dict]:
        bookings = self.booking_manager.get_all_bookings()
        return [self._booking_to_dict(b) for b in bookings]

    def get_meta(self) -> dict:
        locations = self.locations_manager.get_all_locations()
        campaigns = self.campaign_manager.get_campaigns_by_year(date.today().year)
        if not campaigns:
            campaigns = []
            seen_campaigns = set()
            for booking in self.booking_manager.get_all_bookings():
                campaign = self.campaign_manager.get_campaign_by_id(booking.campaign_id)
                if campaign and campaign.campaign_id not in seen_campaigns:
                    campaigns.append(campaign)
                    seen_campaigns.add(campaign.campaign_id)
        cities = self.cities_manager.get_all_cities()
        users = self.user_manager.get_all_users()
        return {
            "locations": [
                {
                    "id": l.location_id,
                    "name": l.name,
                    "price": float(l.price) if l.price is not None else None,
                }
                for l in locations
            ],
            "campaigns": [{"id": c.campaign_id, "name": c.name} for c in campaigns],
            "cities": [{"id": c.city_id, "name": c.name} for c in cities],
            "users": [{"id": u.user_id, "name": f"{u.first_name} {u.last_name}"} for u in users],
            "next_booking_id": self.booking_manager.get_next_booking_id(),
            "next_stand_id": self.locations_manager.get_next_location_id(),
        }

    def create_booking(self, payload: dict) -> dict:
        required = ["date_of_event", "price", "location_id", "campaign_id", "user_id"]
        missing = [key for key in required if payload.get(key) in (None, "")]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")
        booking = self.booking_manager.create_booking(
            date_of_event=date.fromisoformat(str(payload["date_of_event"])),
            price=float(payload["price"]),
            confirmed=self._to_bool(payload.get("confirmed"), default=False),
            location_id=int(payload["location_id"]),
            cancelled=self._to_bool(payload.get("cancelled"), default=False),
            campaign_id=int(payload["campaign_id"]),
            user_id=int(payload["user_id"]),
        )
        return {"id": booking.booking_id}

    def update_booking(self, booking_id: int, payload: dict) -> dict:
        required = ["date_of_event", "price", "location_id", "campaign_id", "user_id"]
        missing = [key for key in required if payload.get(key) in (None, "")]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")
        existing = self.booking_manager.get_booking_by_id(booking_id)
        if not existing:
            raise ValueError(f"Booking {booking_id} not found")
        self.booking_manager.update_booking_fields(
            booking_id=booking_id,
            date_of_event=date.fromisoformat(str(payload["date_of_event"])),
            price=float(payload["price"]),
            confirmed=self._to_bool(payload.get("confirmed"), default=False),
            location_id=int(payload["location_id"]),
            cancelled=self._to_bool(payload.get("cancelled"), default=False),
            campaign_id=int(payload["campaign_id"]),
            user_id=int(payload["user_id"]),
        )
        return {"id": booking_id}

    def create_stand(self, payload: dict) -> dict:
        required = ["name", "max_dialog", "rating", "user_id"]
        missing = [key for key in required if payload.get(key) in (None, "")]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        city_id = self._resolve_city_id(payload)
        user_id = int(payload["user_id"])
        location = self.locations_manager.create_location(
            name=str(payload["name"]).strip(),
            is_sbb=self._to_bool(payload.get("is_sbb"), default=False),
            max_dialog=int(payload["max_dialog"]),
            rating=int(payload["rating"]),
            note=str(payload.get("note") or "") or None,
            price=float(payload["price"]) if payload.get("price") not in (None, "") else None,
            city_id=city_id,
            user_id=user_id,
        )
        self._upsert_location_limits(
            location_id=location.location_id,
            user_id=user_id,
            limit_yearly=self._to_optional_int(payload.get("limit_yearly")),
            limit_monthly=self._to_optional_int(payload.get("limit_monthly")),
            limit_campaign=self._to_optional_int(payload.get("limit_campaign")),
            valid_from=date.fromisoformat(str(payload.get("limit_valid_from"))) if payload.get("limit_valid_from") not in (None, "") else None,
        )
        return {"id": location.location_id}

    def update_stand(self, location_id: int, payload: dict) -> dict:
        required = ["name", "max_dialog", "rating", "user_id"]
        missing = [key for key in required if payload.get(key) in (None, "")]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")
        existing = self.locations_manager.get_location_by_id(location_id)
        if not existing:
            raise ValueError(f"Standplatz {location_id} not found")

        city_id = self._resolve_city_id(payload)
        user_id = int(payload["user_id"])

        self.locations_manager.update_location_fields(
            location_id=location_id,
            name=str(payload["name"]).strip(),
            is_sbb=self._to_bool(payload.get("is_sbb"), default=False),
            max_dialog=int(payload["max_dialog"]),
            rating=int(payload["rating"]),
            note=str(payload.get("note") or "") or None,
            price=float(payload["price"]) if payload.get("price") not in (None, "") else None,
            city_id=city_id,
            user_id=user_id,
        )

        self._upsert_location_limits(
            location_id=location_id,
            user_id=user_id,
            limit_yearly=self._to_optional_int(payload.get("limit_yearly")),
            limit_monthly=self._to_optional_int(payload.get("limit_monthly")),
            limit_campaign=self._to_optional_int(payload.get("limit_campaign")),
            valid_from=date.fromisoformat(str(payload.get("limit_valid_from"))) if payload.get("limit_valid_from") not in (None, "") else None,
        )
        return {"id": location_id}

    def get_stands(self, month_param: str | None = None) -> list[dict]:
        today = date.today()
        selected_year = today.year
        selected_month = today.month
        selected_reference = date(selected_year, selected_month, 1)
        if month_param:
            try:
                y_str, m_str = month_param.split("-")
                year = int(y_str)
                month = int(m_str)
                if 1 <= month <= 12:
                    selected_year = year
                    selected_month = month
                    selected_reference = date(selected_year, selected_month, 1)
            except (ValueError, TypeError):
                pass

        locations = self.locations_manager.get_all_locations()
        bookings = self.booking_manager.get_all_bookings()

        location_map = {location.location_id: location for location in locations}
        location_count_yearly = {}
        location_count_monthly = {}
        location_count_total = {}
        city_count_yearly = {}
        city_count_monthly = {}
        city_count_total = {}

        for booking in bookings:
            if bool(booking.cancelled):
                continue
            location = location_map.get(booking.location_id)
            if not location:
                continue
            booking_date = self._to_date(booking.date_of_event)
            location_id = location.location_id
            city_id = location.city_id
            location_count_total[location_id] = location_count_total.get(location_id, 0) + 1
            city_count_total[city_id] = city_count_total.get(city_id, 0) + 1
            if booking_date.year == selected_year:
                location_count_yearly[location_id] = location_count_yearly.get(location_id, 0) + 1
                city_count_yearly[city_id] = city_count_yearly.get(city_id, 0) + 1
                if booking_date.month == selected_month:
                    location_count_monthly[location_id] = location_count_monthly.get(location_id, 0) + 1
                    city_count_monthly[city_id] = city_count_monthly.get(city_id, 0) + 1

        payload = []
        for location in locations:
            city = self.cities_manager.get_city_by_id(location.city_id)
            state = self.state_manager.get_state_by_id(city.state_id) if city else None

            location_limits = self.location_limit_manager.get_location_limits_by_location_id(location.location_id)
            valid_location_limits = [limit for limit in location_limits if self._to_date(limit.valid_from) <= selected_reference]
            latest_location_limit = max(valid_location_limits, key=lambda x: self._to_date(x.valid_from)) if valid_location_limits else None

            city_limits = self.city_limit_manager.get_city_limits_by_city_name(city.name) if city else []
            valid_city_limits = [limit for limit in city_limits if self._to_date(limit.valid_from) <= selected_reference]
            latest_city_limit = max(valid_city_limits, key=lambda x: self._to_date(x.valid_from)) if valid_city_limits else None

            location_limit_yearly = latest_location_limit.location_limit_yearly if latest_location_limit else None
            location_limit_monthly = latest_location_limit.location_limit_monthly if latest_location_limit else None
            location_limit_campaign = latest_location_limit.location_limit_campaign if latest_location_limit else None

            city_limit_yearly = latest_city_limit.city_limit_yearly if latest_city_limit else None
            city_limit_monthly = latest_city_limit.city_limit_monthly if latest_city_limit else None
            city_limit_campaign = latest_city_limit.city_limit_campaign if latest_city_limit else None

            limit_yearly = location_limit_yearly if location_limit_yearly is not None else city_limit_yearly
            limit_monthly = location_limit_monthly if location_limit_monthly is not None else city_limit_monthly
            limit_campaign = location_limit_campaign if location_limit_campaign is not None else city_limit_campaign

            used_yearly = location_count_yearly.get(location.location_id, 0) if location_limit_yearly is not None else city_count_yearly.get(location.city_id, 0)
            used_monthly = location_count_monthly.get(location.location_id, 0) if location_limit_monthly is not None else city_count_monthly.get(location.city_id, 0)
            used_campaign = location_count_total.get(location.location_id, 0) if location_limit_campaign is not None else city_count_total.get(location.city_id, 0)

            if latest_location_limit and (location_limit_yearly is not None or location_limit_monthly is not None or location_limit_campaign is not None):
                limit_valid_from = str(latest_location_limit.valid_from)
            elif latest_city_limit:
                limit_valid_from = str(latest_city_limit.valid_from)
            else:
                limit_valid_from = None

            if location_limit_yearly is not None and city_limit_yearly is not None and location_limit_yearly == city_limit_yearly:
                used_yearly = city_count_yearly.get(location.city_id, 0)
            if location_limit_monthly is not None and city_limit_monthly is not None and location_limit_monthly == city_limit_monthly:
                used_monthly = city_count_monthly.get(location.city_id, 0)
            if location_limit_campaign is not None and city_limit_campaign is not None and location_limit_campaign == city_limit_campaign:
                used_campaign = city_count_total.get(location.city_id, 0)

            payload.append(
                {
                    "id": location.location_id,
                    "name": location.name,
                    "is_sbb": bool(location.is_sbb),
                    "max_dialog": location.max_dialog,
                    "rating": location.rating,
                    "note": location.note,
                    "price": float(location.price) if location.price is not None else None,
                    "city_id": location.city_id,
                    "user_id": location.user_id,
                    "city": city.name if city else f"City {location.city_id}",
                    "kanton": state.name if state else None,
                    "limit_yearly": limit_yearly,
                    "limit_monthly": limit_monthly,
                    "limit_campaign": limit_campaign,
                    "limit_valid_from": limit_valid_from,
                    "location_limit_yearly_raw": location_limit_yearly,
                    "location_limit_monthly_raw": location_limit_monthly,
                    "location_limit_campaign_raw": location_limit_campaign,
                    "location_limit_valid_from_raw": str(latest_location_limit.valid_from) if latest_location_limit else None,
                    "remaining_yearly": max(limit_yearly - used_yearly, 0) if limit_yearly is not None else None,
                    "remaining_monthly": max(limit_monthly - used_monthly, 0) if limit_monthly is not None else None,
                    "remaining_campaign": max(limit_campaign - used_campaign, 0) if limit_campaign is not None else None,
                }
            )

        return payload
