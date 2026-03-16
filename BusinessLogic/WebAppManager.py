from datetime import date, datetime

from DataAccess.AddressDataAccess import AddressDataAccess
from BusinessLogic.BookingManager import BookingManager
from BusinessLogic.CampaignManager import CampaignManager
from BusinessLogic.CitiesManager import CitiesManager
from BusinessLogic.CityLimitManager import CityLimitManager
from BusinessLogic.ContactInformationManager import ContactInformationManager
from BusinessLogic.LocationsLimitManager import LocationsLimitManager
from BusinessLogic.LocationsManager import LocationsManager
from BusinessLogic.StateManager import StateManager
from BusinessLogic.UserManager import UserManager


class WebAppManager:
    def __init__(self, db_path: str):
        self.booking_manager = BookingManager(db_path)
        self.address_dao = AddressDataAccess(db_path)
        self.campaign_manager = CampaignManager(db_path)
        self.cities_manager = CitiesManager(db_path)
        self.city_limit_manager = CityLimitManager(db_path)
        self.contact_information_manager = ContactInformationManager(db_path)
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

    @staticmethod
    def _normalize_email(value: str) -> str:
        return str(value or "").strip().lower()

    @staticmethod
    def _validate_email(email: str) -> None:
        if not email:
            raise ValueError("E-Mail ist ein Pflichtfeld.")
        if "@" not in email or "." not in email:
            raise ValueError("E-Mail hat kein gueltiges Format.")

    def _upsert_user_contact_information(self, user_id: int, email: str, phone: str | None) -> None:
        normalized_email = self._normalize_email(email)
        self._validate_email(normalized_email)
        phone_value = str(phone).strip() if phone not in (None, "") else None

        existing_for_user = self.contact_information_manager.get_contact_information_by_user(user_id)
        if existing_for_user:
            primary = existing_for_user[0]
            primary.e_mail = normalized_email
            primary.phone = phone_value
            self.contact_information_manager.update_contact_information(primary)
            return

        self.contact_information_manager.create_contact_information(
            email=normalized_email,
            phone=phone_value,
            user_id=user_id,
        )

    def _upsert_user_address(self, user_id: int, payload: dict) -> None:
        street = str(payload.get("address_street") or "").strip()
        number = str(payload.get("address_number") or "").strip()
        zip_code = str(payload.get("address_zip") or "").strip()
        city = str(payload.get("address_city") or "").strip()
        state_name = str(payload.get("address_state") or "").strip()

        state_id = None
        if state_name:
            state = self.state_manager.get_state_by_name(state_name)
            if not state:
                state = self.state_manager.create_state(state_name)
            state_id = state.state_id

        has_any = any([street, number, zip_code, city, state_name])
        existing = self.address_dao.get_addresses_by_user_id(user_id)
        if not has_any:
            for addr in existing:
                self.address_dao.delete_address(addr.address_id)
            return

        if existing:
            primary_id = existing[0].address_id
            self.address_dao.execute(
                "UPDATE Address SET Street = ?, Number = ?, Zip = ?, City = ?, StateID = ?, UserID = ? WHERE AddressID = ?",
                (
                    street or None,
                    number or None,
                    zip_code or None,
                    city or None,
                    state_id,
                    user_id,
                    primary_id,
                ),
            )
            return

        self.address_dao.execute(
            "INSERT INTO Address (Street, Number, Zip, City, StateID, UserID) VALUES (?, ?, ?, ?, ?, ?)",
            (
                street or None,
                number or None,
                zip_code or None,
                city or None,
                state_id,
                user_id,
            ),
        )

    def _resolve_campaign_id(
        self,
        payload: dict,
        fallback_user_id: int,
        fallback_event_date: date,
    ) -> int:
        campaign_id_raw = payload.get("campaign_id")
        if campaign_id_raw not in (None, ""):
            return int(campaign_id_raw)

        campaign_name = str(payload.get("campaign_name") or "").strip()
        if not campaign_name:
            raise ValueError("Missing fields: campaign_id")

        create_if_missing = self._to_bool(payload.get("create_campaign_if_missing"), default=False)
        campaign_year = self._to_optional_int(payload.get("campaign_year")) or fallback_event_date.year
        campaign_user_id = self._to_optional_int(payload.get("campaign_user_id")) or fallback_user_id
        campaign_budget_raw = payload.get("campaign_budget")
        campaign_budget = float(campaign_budget_raw) if campaign_budget_raw not in (None, "") else 0.0

        campaigns = self.campaign_manager.get_campaigns_by_name(campaign_name)
        for campaign in campaigns:
            if int(campaign.year) == int(campaign_year):
                return campaign.campaign_id
        if campaigns and not create_if_missing:
            return campaigns[0].campaign_id

        if not create_if_missing:
            raise ValueError("Kampagne nicht gefunden.")

        new_campaign = self.campaign_manager.create_campaign(
            name=campaign_name,
            year=int(campaign_year),
            budget=campaign_budget,
            user_id=int(campaign_user_id),
        )
        return new_campaign.campaign_id

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

    def _validate_booking_limits(
        self,
        location_id: int,
        event_date: date,
        campaign_id: int,
        exclude_booking_id: int | None = None,
    ) -> None:
        location = self.locations_manager.get_location_by_id(location_id)
        if not location:
            raise ValueError("Standplatz nicht gefunden.")

        city = self.cities_manager.get_city_by_id(location.city_id)
        selected_reference = date(event_date.year, event_date.month, 1)

        location_limits = self.location_limit_manager.get_location_limits_by_location_id(location_id)
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

        effective_yearly = location_limit_yearly if location_limit_yearly is not None else city_limit_yearly
        effective_monthly = location_limit_monthly if location_limit_monthly is not None else city_limit_monthly
        effective_campaign = location_limit_campaign if location_limit_campaign is not None else city_limit_campaign

        bookings = self.booking_manager.get_all_bookings()
        scoped = []
        for booking in bookings:
            if bool(booking.cancelled):
                continue
            if exclude_booking_id is not None and int(booking.booking_id) == int(exclude_booking_id):
                continue
            scoped.append(booking)

        location_yearly_count = sum(
            1 for booking in scoped
            if int(booking.location_id) == int(location_id)
            and self._to_date(booking.date_of_event).year == event_date.year
        )
        location_monthly_count = sum(
            1 for booking in scoped
            if int(booking.location_id) == int(location_id)
            and self._to_date(booking.date_of_event).year == event_date.year
            and self._to_date(booking.date_of_event).month == event_date.month
        )
        location_campaign_count = sum(
            1 for booking in scoped
            if int(booking.location_id) == int(location_id)
            and int(booking.campaign_id) == int(campaign_id)
        )

        city_yearly_count = 0
        city_monthly_count = 0
        city_campaign_count = 0
        if city:
            for booking in scoped:
                booking_location = self.locations_manager.get_location_by_id(booking.location_id)
                if not booking_location or int(booking_location.city_id) != int(city.city_id):
                    continue
                booking_date = self._to_date(booking.date_of_event)
                if booking_date.year == event_date.year:
                    city_yearly_count += 1
                    if booking_date.month == event_date.month:
                        city_monthly_count += 1
                if int(booking.campaign_id) == int(campaign_id):
                    city_campaign_count += 1

        used_yearly = location_yearly_count if location_limit_yearly is not None else city_yearly_count
        used_monthly = location_monthly_count if location_limit_monthly is not None else city_monthly_count
        used_campaign = location_campaign_count if location_limit_campaign is not None else city_campaign_count

        if effective_yearly is not None and used_yearly >= int(effective_yearly):
            raise ValueError(f"Jahreslimit erreicht ({used_yearly}/{effective_yearly}).")
        if effective_monthly is not None and used_monthly >= int(effective_monthly):
            raise ValueError(f"Monatslimit erreicht ({used_monthly}/{effective_monthly}).")
        if effective_campaign is not None and used_campaign >= int(effective_campaign):
            raise ValueError(f"Kampagnenlimit erreicht ({used_campaign}/{effective_campaign}).")

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

    def get_campaigns(self) -> list[dict]:
        campaigns = self.campaign_manager.get_all_campaigns()
        users = {u.user_id: f"{u.first_name} {u.last_name}" for u in self.user_manager.get_all_users()}
        return [
            {
                "id": c.campaign_id,
                "name": c.name,
                "year": int(c.year),
                "budget": float(c.budget) if c.budget is not None else 0.0,
                "user_id": c.user_id,
                "user_name": users.get(c.user_id, f"User {c.user_id}"),
                "is_active": bool(c.is_active),
            }
            for c in campaigns
        ]

    def get_users(self) -> list[dict]:
        users = self.user_manager.get_all_users()
        contacts_by_user = {}
        for info in self.contact_information_manager.contact_information_dao.fetchall(
            "SELECT ContactInformationID, EMail, Phone, UserID FROM ContactInformation ORDER BY ContactInformationID"
        ):
            contact_id, email, phone, user_id = info
            user_key = int(user_id)
            if user_key in contacts_by_user:
                continue
            contacts_by_user[user_key] = {"email": email, "phone": phone, "contact_id": contact_id}
        addresses_by_user = {}
        for info in self.address_dao.fetchall(
            "SELECT a.AddressID, a.Street, a.Number, a.Zip, a.City, a.StateID, a.UserID, s.Name FROM Address a LEFT JOIN States s ON s.StateID = a.StateID ORDER BY a.AddressID"
        ):
            address_id, street, number, zip_code, city, state_id, user_id, state_name = info
            user_key = int(user_id)
            if user_key in addresses_by_user:
                continue
            addresses_by_user[user_key] = {
                "address_id": address_id,
                "street": street,
                "number": number,
                "zip": zip_code,
                "city": city,
                "state_id": state_id,
                "state_name": state_name,
            }
        return [
            {
                "id": u.user_id,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "full_name": f"{u.first_name} {u.last_name}".strip(),
                "role": u.role,
                "is_active": bool(u.is_active),
                "email": contacts_by_user.get(int(u.user_id), {}).get("email") or "",
                "phone": contacts_by_user.get(int(u.user_id), {}).get("phone") or "",
                "address_street": addresses_by_user.get(int(u.user_id), {}).get("street") or "",
                "address_number": addresses_by_user.get(int(u.user_id), {}).get("number") or "",
                "address_zip": addresses_by_user.get(int(u.user_id), {}).get("zip") or "",
                "address_city": addresses_by_user.get(int(u.user_id), {}).get("city") or "",
                "address_state": addresses_by_user.get(int(u.user_id), {}).get("state_name") or "",
            }
            for u in users
        ]

    def get_meta(self) -> dict:
        locations = self.locations_manager.get_all_locations()
        campaigns = self.campaign_manager.get_campaigns_by_year(date.today().year) or []
        seen_campaigns = {c.campaign_id for c in campaigns}
        for booking in self.booking_manager.get_all_bookings():
            campaign = self.campaign_manager.get_campaign_by_id(booking.campaign_id)
            if campaign and campaign.campaign_id not in seen_campaigns:
                campaigns.append(campaign)
                seen_campaigns.add(campaign.campaign_id)
        cities = self.cities_manager.get_all_cities()
        users = self.user_manager.get_all_users()
        location_payload = []
        for location in locations:
            city = self.cities_manager.get_city_by_id(location.city_id)
            location_payload.append(
                {
                    "id": location.location_id,
                    "name": location.name,
                    "city": city.name if city else "",
                    "price": float(location.price) if location.price is not None else None,
                }
            )

        return {
            "locations": location_payload,
            "campaigns": [
                {
                    "id": c.campaign_id,
                    "name": c.name,
                    "year": int(c.year),
                    "budget": float(c.budget) if c.budget is not None else 0.0,
                    "user_id": c.user_id,
                    "is_active": bool(c.is_active),
                }
                for c in campaigns
            ],
            "cities": [{"id": c.city_id, "name": c.name} for c in cities],
            "users": [
                {
                    "id": u.user_id,
                    "name": f"{u.first_name} {u.last_name}",
                    "first_name": u.first_name,
                    "last_name": u.last_name,
                    "role": u.role,
                    "is_active": bool(u.is_active),
                    "email": next(
                        (
                            ci.e_mail
                            for ci in self.contact_information_manager.get_contact_information_by_user(u.user_id)
                        ),
                        "",
                    ),
                    "address": next(
                        (a.street for a in self.address_dao.get_addresses_by_user_id(u.user_id) if a.street),
                        "",
                    ),
                }
                for u in users
            ],
            "next_booking_id": self.booking_manager.get_next_booking_id(),
            "next_stand_id": self.locations_manager.get_next_location_id(),
        }

    def create_booking(self, payload: dict) -> dict:
        required = ["date_of_event", "price", "location_id", "user_id"]
        missing = [key for key in required if payload.get(key) in (None, "")]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")
        event_date = date.fromisoformat(str(payload["date_of_event"]))
        user_id = int(payload["user_id"])
        campaign_id = self._resolve_campaign_id(
            payload=payload,
            fallback_user_id=user_id,
            fallback_event_date=event_date,
        )
        self._validate_booking_limits(
            location_id=int(payload["location_id"]),
            event_date=event_date,
            campaign_id=campaign_id,
        )
        booking = self.booking_manager.create_booking(
            date_of_event=event_date,
            price=float(payload["price"]),
            confirmed=self._to_bool(payload.get("confirmed"), default=False),
            location_id=int(payload["location_id"]),
            cancelled=self._to_bool(payload.get("cancelled"), default=False),
            campaign_id=campaign_id,
            user_id=user_id,
        )
        return {"id": booking.booking_id}

    def validate_booking(self, payload: dict, booking_id: int | None = None) -> dict:
        required = ["date_of_event", "price", "location_id", "user_id"]
        missing = [key for key in required if payload.get(key) in (None, "")]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        event_date = date.fromisoformat(str(payload["date_of_event"]))
        location_id = int(payload["location_id"])
        user_id = int(payload["user_id"])
        payload_for_resolve = dict(payload)
        payload_for_resolve["create_campaign_if_missing"] = False
        campaign_id = self._resolve_campaign_id(
            payload=payload_for_resolve,
            fallback_user_id=user_id,
            fallback_event_date=event_date,
        )

        # Keep same core checks as create/update, but without persisting.
        self.booking_manager._validate_booking_data(
            date_of_event=event_date,
            price=float(payload["price"]),
            location_id=location_id,
            campaign_id=campaign_id,
            user_id=user_id,
        )
        location = self.locations_manager.get_location_by_id(location_id)
        if not location:
            raise ValueError("Standort existiert nicht")

        if not self.booking_manager._is_location_available(
            location_id=location_id,
            event_date=event_date,
            exclude_booking_id=booking_id,
        ):
            raise ValueError("Standort ist an diesem Datum nicht verfuegbar")

        if not self.booking_manager._is_price_valid(float(payload["price"]), location):
            raise ValueError("Preis liegt ausserhalb des erlaubten Bereichs")

        self._validate_booking_limits(
            location_id=location_id,
            event_date=event_date,
            campaign_id=campaign_id,
            exclude_booking_id=booking_id,
        )
        return {"ok": True}

    def validate_booking_limits_only(self, payload: dict, booking_id: int | None = None) -> dict:
        required = ["date_of_event", "location_id"]
        missing = [key for key in required if payload.get(key) in (None, "")]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        event_date = date.fromisoformat(str(payload["date_of_event"]))
        location_id = int(payload["location_id"])
        campaign_id_raw = payload.get("campaign_id")
        campaign_id = int(campaign_id_raw) if campaign_id_raw not in (None, "") else 0

        self._validate_booking_limits(
            location_id=location_id,
            event_date=event_date,
            campaign_id=campaign_id,
            exclude_booking_id=booking_id,
        )
        return {"ok": True}

    def create_campaign(self, payload: dict) -> dict:
        required = ["name", "year", "budget", "user_id"]
        missing = [key for key in required if payload.get(key) in (None, "")]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        campaign = self.campaign_manager.create_campaign(
            name=str(payload["name"]).strip(),
            year=int(payload["year"]),
            budget=float(payload["budget"]),
            user_id=int(payload["user_id"]),
            is_active=self._to_bool(payload.get("is_active"), default=True),
        )
        return {"id": campaign.campaign_id, "name": campaign.name}

    def update_campaign(self, campaign_id: int, payload: dict) -> dict:
        required = ["name", "year", "budget", "user_id"]
        missing = [key for key in required if payload.get(key) in (None, "")]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        existing = self.campaign_manager.get_campaign_by_id(campaign_id)
        if not existing:
            raise ValueError(f"Campaign {campaign_id} not found")

        existing.name = str(payload["name"]).strip()
        existing.year = int(payload["year"])
        existing.budget = float(payload["budget"])
        existing.user_id = int(payload["user_id"])
        if "is_active" in payload:
            existing.is_active = self._to_bool(payload.get("is_active"), default=True)
        self.campaign_manager.update_campaign(existing)
        return {"id": campaign_id, "name": existing.name}

    def delete_campaign(self, campaign_id: int) -> dict:
        existing = self.campaign_manager.get_campaign_by_id(campaign_id)
        if not existing:
            raise ValueError(f"Campaign {campaign_id} not found")

        linked_bookings = self.booking_manager.get_bookings_by_campaign(campaign_id)
        if linked_bookings:
            raise ValueError(
                f"Kampagne kann nicht geloescht werden: {len(linked_bookings)} Buchung(en) sind verknuepft."
            )

        self.campaign_manager.delete_campaign(campaign_id)
        return {"id": campaign_id, "deleted": True}

    def create_user(self, payload: dict) -> dict:
        required = ["first_name", "last_name", "password", "role", "email"]
        missing = [key for key in required if payload.get(key) in (None, "")]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        user = self.user_manager.create_user(
            last_name=str(payload["last_name"]).strip(),
            first_name=str(payload["first_name"]).strip(),
            password=str(payload["password"]),
            role=str(payload["role"]).strip(),
            is_active=self._to_bool(payload.get("is_active"), default=True),
        )
        self._upsert_user_contact_information(
            user_id=user.user_id,
            email=str(payload.get("email") or ""),
            phone=payload.get("phone"),
        )
        self._upsert_user_address(user.user_id, payload)
        return {"id": user.user_id, "name": f"{user.first_name} {user.last_name}"}

    def update_user(self, user_id: int, payload: dict) -> dict:
        required = ["first_name", "last_name", "role"]
        missing = [key for key in required if payload.get(key) in (None, "")]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        existing = self.user_manager.get_user_by_id(user_id)
        if not existing:
            raise ValueError(f"User {user_id} not found")

        existing.first_name = str(payload["first_name"]).strip()
        existing.last_name = str(payload["last_name"]).strip()
        existing.role = str(payload["role"]).strip()
        if payload.get("password") not in (None, ""):
            existing.password = str(payload["password"])
        if "is_active" in payload:
            existing.is_active = self._to_bool(payload.get("is_active"), default=True)
        self.user_manager.update_user(existing)
        if payload.get("email") not in (None, ""):
            self._upsert_user_contact_information(
                user_id=user_id,
                email=str(payload.get("email") or ""),
                phone=payload.get("phone"),
            )
        if any(key in payload for key in ["address_street", "address_number", "address_zip", "address_city", "address_state"]):
            self._upsert_user_address(user_id, payload)
        return {"id": user_id, "name": f"{existing.first_name} {existing.last_name}"}

    def delete_user(self, user_id: int) -> dict:
        existing = self.user_manager.get_user_by_id(user_id)
        if not existing:
            raise ValueError(f"User {user_id} not found")

        linked_bookings = self.booking_manager.get_bookings_by_user(user_id)
        if linked_bookings:
            raise ValueError(
                f"Benutzer kann nicht geloescht werden: {len(linked_bookings)} Buchung(en) sind verknuepft."
            )

        linked_stands = self.locations_manager.get_locations_by_user(user_id)
        if linked_stands:
            raise ValueError(
                f"Benutzer kann nicht geloescht werden: {len(linked_stands)} Standplatz/Standplaetze sind verknuepft."
            )

        for ci in self.contact_information_manager.get_contact_information_by_user(user_id):
            self.contact_information_manager.delete_contact_information(ci.contact_information_id)
        for addr in self.address_dao.get_addresses_by_user_id(user_id):
            self.address_dao.delete_address(addr.address_id)

        self.user_manager.delete_user(user_id)
        return {"id": user_id, "deleted": True}

    def update_booking(self, booking_id: int, payload: dict) -> dict:
        required = ["date_of_event", "price", "location_id", "user_id"]
        missing = [key for key in required if payload.get(key) in (None, "")]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")
        existing = self.booking_manager.get_booking_by_id(booking_id)
        if not existing:
            raise ValueError(f"Booking {booking_id} not found")
        event_date = date.fromisoformat(str(payload["date_of_event"]))
        user_id = int(payload["user_id"])
        campaign_id = self._resolve_campaign_id(
            payload=payload,
            fallback_user_id=user_id,
            fallback_event_date=event_date,
        )
        self._validate_booking_limits(
            location_id=int(payload["location_id"]),
            event_date=event_date,
            campaign_id=campaign_id,
            exclude_booking_id=booking_id,
        )
        self.booking_manager.update_booking_fields(
            booking_id=booking_id,
            date_of_event=event_date,
            price=float(payload["price"]),
            confirmed=self._to_bool(payload.get("confirmed"), default=False),
            location_id=int(payload["location_id"]),
            cancelled=self._to_bool(payload.get("cancelled"), default=False),
            campaign_id=campaign_id,
            user_id=user_id,
        )
        return {"id": booking_id}

    def delete_booking(self, booking_id: int) -> dict:
        existing = self.booking_manager.get_booking_by_id(booking_id)
        if not existing:
            raise ValueError(f"Booking {booking_id} not found")
        self.booking_manager.delete_booking(booking_id)
        return {"id": booking_id, "deleted": True}

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

    def delete_stand(self, location_id: int) -> dict:
        existing = self.locations_manager.get_location_by_id(location_id)
        if not existing:
            raise ValueError(f"Standplatz {location_id} not found")

        linked_bookings = self.booking_manager.get_bookings_by_location(location_id)
        if linked_bookings:
            raise ValueError(
                f"Standplatz kann nicht geloescht werden: {len(linked_bookings)} Buchung(en) sind verknuepft."
            )

        # Cleanup limits for this stand before deleting the stand itself.
        self.location_limit_manager.location_limit_dao.execute(
            "DELETE FROM LocationLimits WHERE LocationID = ?",
            (location_id,),
        )
        self.locations_manager.delete_location(location_id)
        return {"id": location_id, "deleted": True}

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
