import json
import sys
import argparse
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from DataAccess.BookingDataAccess import BookingDataAccess
from DataAccess.CampaignDataAccess import CampaignDataAccess
from DataAccess.CitiesDataAccess import CitiesDataAccess
from DataAccess.CityLimitDataAccess import CityLimitDataAccess
from DataAccess.LocationLimitsDataAccess import LocationLimitsDataAccess
from DataAccess.LocationsDataAccess import LocationsDataAccess
from DataAccess.StateDataAccess import StateDataAccess
from DataAccess.UserDataAccess import UserDataAccess


UI_ROOT = PROJECT_ROOT / "UI"
DB_PATH = str(PROJECT_ROOT / "Databank" / "StandplaetzeDatabank.db")


def _to_bool(value, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "ja", "on"}


def _to_date(value) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    return date.fromisoformat(str(value))


def _booking_to_dict(booking, location_dao: LocationsDataAccess, campaign_dao: CampaignDataAccess) -> dict:
    location = location_dao.get_location_by_id(booking.location_id)
    campaign = campaign_dao.get_campaign_by_id(booking.campaign_id)
    city_name = None
    if location:
        city = CitiesDataAccess(DB_PATH).get_city_by_id(location.city_id)
        city_name = city.name if city else None
    created_at = _to_date(booking.date_of_booking)
    event_date = _to_date(booking.date_of_event)
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


class RequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict | list, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, filepath: Path, content_type: str) -> None:
        if not filepath.exists():
            self.send_error(404, "File not found")
            return
        data = filepath.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw) if raw else {}

    def _get_next_id(self, dao, table_name: str, id_column: str) -> int:
        seq_row = dao.fetchone("SELECT seq FROM sqlite_sequence WHERE name = ?", (table_name,))
        if seq_row and seq_row[0] is not None:
            return int(seq_row[0]) + 1
        max_row = dao.fetchone(f"SELECT MAX({id_column}) FROM {table_name}")
        max_value = max_row[0] if max_row else None
        return (int(max_value) + 1) if max_value is not None else 1

    def _resolve_city_id(self, payload: dict) -> int:
        cities_dao = CitiesDataAccess(DB_PATH)
        states_dao = StateDataAccess(DB_PATH)

        city_id_raw = payload.get("city_id")
        city_name = str(payload.get("city_name") or "").strip()
        kanton_name = str(payload.get("kanton_name") or "").strip()

        if city_id_raw not in (None, ""):
            return int(city_id_raw)

        if not city_name:
            raise ValueError("Missing fields: city_name")

        cities = cities_dao.get_city_by_name(city_name)
        existing_city = None
        for city in cities:
            if city.name.strip().lower() == city_name.lower():
                existing_city = city
                break

        if existing_city:
            return existing_city.city_id

        if not kanton_name:
            raise ValueError("Fuer neue Staedte ist ein Kanton erforderlich.")

        state = states_dao.get_state_by_name(kanton_name)
        if not state:
            state = states_dao.insert_state(kanton_name)

        new_city = cities_dao.insert_city(city_name, state.state_id)
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
        limits_dao = LocationLimitsDataAccess(DB_PATH)

        sql_find = """
        SELECT LocationLimitID
        FROM LocationLimits
        WHERE LocationID = ? AND ValidFrom = ?
        """
        row = limits_dao.fetchone(sql_find, (location_id, effective_valid_from))
        if row:
            sql_update = """
            UPDATE LocationLimits
            SET LocationLimitYearly = ?, LocationLimitMonthly = ?, LocationLimitCampaign = ?, UserID = ?
            WHERE LocationLimitID = ?
            """
            limits_dao.execute(
                sql_update,
                (limit_yearly, limit_monthly, limit_campaign, user_id, int(row[0])),
            )
            return

        sql = """
        INSERT INTO LocationLimits (LocationLimitYearly, LocationLimitMonthly, LocationLimitCampaign,
                                    LocationID, ValidFrom, UserID)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        limits_dao.execute(sql, (limit_yearly, limit_monthly, limit_campaign, location_id, effective_valid_from, user_id))

    def _handle_dashboard(self) -> None:
        booking_dao = BookingDataAccess(DB_PATH)
        bookings = booking_dao.get_all_bookings()
        total = len(bookings)
        confirmed = sum(1 for b in bookings if bool(b.confirmed) and not bool(b.cancelled))
        open_bookings = sum(1 for b in bookings if not bool(b.confirmed) and not bool(b.cancelled))
        revenue = sum(float(b.price or 0.0) for b in bookings if bool(b.confirmed) and not bool(b.cancelled))
        self._send_json(
            {
                "total": total,
                "confirmed": confirmed,
                "open": open_bookings,
                "revenue": round(revenue, 2),
            }
        )

    def _handle_bookings(self) -> None:
        booking_dao = BookingDataAccess(DB_PATH)
        location_dao = LocationsDataAccess(DB_PATH)
        campaign_dao = CampaignDataAccess(DB_PATH)
        bookings = booking_dao.get_all_bookings()
        payload = [_booking_to_dict(b, location_dao, campaign_dao) for b in bookings]
        self._send_json(payload)

    def _handle_meta(self) -> None:
        locations = LocationsDataAccess(DB_PATH).get_all_locations()
        booking_dao = BookingDataAccess(DB_PATH)
        locations_dao = LocationsDataAccess(DB_PATH)
        campaigns_dao = CampaignDataAccess(DB_PATH)
        campaigns = campaigns_dao.get_campaign_by_year(date.today().year)
        if not campaigns:
            campaigns = []
            seen_campaigns = set()
            for booking in BookingDataAccess(DB_PATH).get_all_bookings():
                campaign = campaigns_dao.get_campaign_by_id(booking.campaign_id)
                if campaign and campaign.campaign_id not in seen_campaigns:
                    campaigns.append(campaign)
                    seen_campaigns.add(campaign.campaign_id)

        cities = CitiesDataAccess(DB_PATH).get_all_cities()
        users = UserDataAccess(DB_PATH).get_all_users()

        payload = {
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
            "next_booking_id": self._get_next_id(booking_dao, "Bookings", "BookingID"),
            "next_stand_id": self._get_next_id(locations_dao, "Locations", "LocationID"),
        }
        self._send_json(payload)

    def _handle_create_booking(self) -> None:
        payload = self._read_json_body()

        required = ["date_of_event", "price", "location_id", "campaign_id", "user_id"]
        missing = [key for key in required if payload.get(key) in (None, "")]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        booking = BookingDataAccess(DB_PATH).insert_booking(
            date_of_event=date.fromisoformat(str(payload["date_of_event"])),
            price=float(payload["price"]),
            confirmed=_to_bool(payload.get("confirmed"), default=False),
            location_id=int(payload["location_id"]),
            cancelled=_to_bool(payload.get("cancelled"), default=False),
            campaign_id=int(payload["campaign_id"]),
            user_id=int(payload["user_id"]),
        )
        self._send_json({"id": booking.booking_id}, status=201)

    def _handle_create_stand(self) -> None:
        payload = self._read_json_body()

        required = ["name", "max_dialog", "rating", "user_id"]
        missing = [key for key in required if payload.get(key) in (None, "")]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        city_id = self._resolve_city_id(payload)

        location = LocationsDataAccess(DB_PATH).insert_location(
            name=str(payload["name"]).strip(),
            is_sbb=_to_bool(payload.get("is_sbb"), default=False),
            max_dialog=int(payload["max_dialog"]),
            rating=int(payload["rating"]),
            note=str(payload.get("note") or "") or None,
            price=float(payload["price"]) if payload.get("price") not in (None, "") else None,
            city_id=city_id,
            user_id=int(payload["user_id"]),
        )

        def _to_optional_int(value):
            if value in (None, ""):
                return None
            return int(value)

        limit_yearly = _to_optional_int(payload.get("limit_yearly"))
        limit_monthly = _to_optional_int(payload.get("limit_monthly"))
        limit_campaign = _to_optional_int(payload.get("limit_campaign"))
        limit_valid_from = payload.get("limit_valid_from")

        self._upsert_location_limits(
            location_id=location.location_id,
            user_id=int(payload["user_id"]),
            limit_yearly=limit_yearly,
            limit_monthly=limit_monthly,
            limit_campaign=limit_campaign,
            valid_from=date.fromisoformat(str(limit_valid_from)) if limit_valid_from not in (None, "") else None,
        )

        self._send_json({"id": location.location_id}, status=201)

    def _handle_update_booking(self, booking_id: int) -> None:
        payload = self._read_json_body()
        required = ["date_of_event", "price", "location_id", "campaign_id", "user_id"]
        missing = [key for key in required if payload.get(key) in (None, "")]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        booking_dao = BookingDataAccess(DB_PATH)
        existing = booking_dao.get_booking_by_id(booking_id)
        if not existing:
            raise ValueError(f"Booking {booking_id} not found")

        sql = """
        UPDATE Bookings
        SET DateOfEvent = ?, DateOfLastUpdate = ?, Price = ?, Confirmed = ?,
            LocationID = ?, Cancelled = ?, CampaignID = ?, UserID = ?
        WHERE BookingID = ?
        """
        booking_dao.execute(
            sql,
            (
                date.fromisoformat(str(payload["date_of_event"])),
                date.today(),
                float(payload["price"]),
                _to_bool(payload.get("confirmed"), default=False),
                int(payload["location_id"]),
                _to_bool(payload.get("cancelled"), default=False),
                int(payload["campaign_id"]),
                int(payload["user_id"]),
                booking_id,
            ),
        )
        self._send_json({"id": booking_id}, status=200)

    def _handle_update_stand(self, location_id: int) -> None:
        payload = self._read_json_body()
        required = ["name", "max_dialog", "rating", "user_id"]
        missing = [key for key in required if payload.get(key) in (None, "")]
        if missing:
            raise ValueError(f"Missing fields: {', '.join(missing)}")

        city_id = self._resolve_city_id(payload)
        user_id = int(payload["user_id"])

        location_dao = LocationsDataAccess(DB_PATH)
        existing = location_dao.get_location_by_id(location_id)
        if not existing:
            raise ValueError(f"Standplatz {location_id} not found")

        sql = """
        UPDATE Locations
        SET Name = ?, IsSBB = ?, MaxDialog = ?, Rating = ?, Notes = ?, Price = ?, CityID = ?, UserID = ?
        WHERE LocationID = ?
        """
        location_dao.execute(
            sql,
            (
                str(payload["name"]).strip(),
                _to_bool(payload.get("is_sbb"), default=False),
                int(payload["max_dialog"]),
                int(payload["rating"]),
                str(payload.get("note") or "") or None,
                float(payload["price"]) if payload.get("price") not in (None, "") else None,
                city_id,
                user_id,
                location_id,
            ),
        )

        def _to_optional_int(value):
            if value in (None, ""):
                return None
            return int(value)

        self._upsert_location_limits(
            location_id=location_id,
            user_id=user_id,
            limit_yearly=_to_optional_int(payload.get("limit_yearly")),
            limit_monthly=_to_optional_int(payload.get("limit_monthly")),
            limit_campaign=_to_optional_int(payload.get("limit_campaign")),
            valid_from=date.fromisoformat(str(payload.get("limit_valid_from"))) if payload.get("limit_valid_from") not in (None, "") else None,
        )
        self._send_json({"id": location_id}, status=200)

    def _handle_stands(self, month_param: str | None = None) -> None:
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

        locations_dao = LocationsDataAccess(DB_PATH)
        cities_dao = CitiesDataAccess(DB_PATH)
        states_dao = StateDataAccess(DB_PATH)
        city_limits_dao = CityLimitDataAccess(DB_PATH)
        location_limits_dao = LocationLimitsDataAccess(DB_PATH)
        booking_dao = BookingDataAccess(DB_PATH)

        locations = locations_dao.get_all_locations()
        bookings = booking_dao.get_all_bookings()

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

            booking_date = _to_date(booking.date_of_event)
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
            city = cities_dao.get_city_by_id(location.city_id)
            state = states_dao.get_state_by_id(city.state_id) if city else None
            location_limits = location_limits_dao.get_location_limits_by_location_id(location.location_id)
            valid_location_limits = [
                limit for limit in location_limits if _to_date(limit.valid_from) <= selected_reference
            ]
            latest_location_limit = (
                max(valid_location_limits, key=lambda x: _to_date(x.valid_from))
                if valid_location_limits
                else None
            )

            city_limits = city_limits_dao.get_city_limit_by_city_name(city.name) if city else []
            valid_city_limits = [
                limit for limit in city_limits if _to_date(limit.valid_from) <= selected_reference
            ]
            latest_city_limit = (
                max(valid_city_limits, key=lambda x: _to_date(x.valid_from))
                if valid_city_limits
                else None
            )

            location_limit_yearly = latest_location_limit.location_limit_yearly if latest_location_limit else None
            location_limit_monthly = latest_location_limit.location_limit_monthly if latest_location_limit else None
            location_limit_campaign = latest_location_limit.location_limit_campaign if latest_location_limit else None

            city_limit_yearly = latest_city_limit.city_limit_yearly if latest_city_limit else None
            city_limit_monthly = latest_city_limit.city_limit_monthly if latest_city_limit else None
            city_limit_campaign = latest_city_limit.city_limit_campaign if latest_city_limit else None

            limit_yearly = location_limit_yearly if location_limit_yearly is not None else city_limit_yearly
            limit_monthly = location_limit_monthly if location_limit_monthly is not None else city_limit_monthly
            limit_campaign = location_limit_campaign if location_limit_campaign is not None else city_limit_campaign

            used_yearly = (
                location_count_yearly.get(location.location_id, 0)
                if location_limit_yearly is not None
                else city_count_yearly.get(location.city_id, 0)
            )
            used_monthly = (
                location_count_monthly.get(location.location_id, 0)
                if location_limit_monthly is not None
                else city_count_monthly.get(location.city_id, 0)
            )
            used_campaign = (
                location_count_total.get(location.location_id, 0)
                if location_limit_campaign is not None
                else city_count_total.get(location.city_id, 0)
            )

            if latest_location_limit and (
                location_limit_yearly is not None
                or location_limit_monthly is not None
                or location_limit_campaign is not None
            ):
                limit_valid_from = str(latest_location_limit.valid_from)
            elif latest_city_limit:
                limit_valid_from = str(latest_city_limit.valid_from)
            else:
                limit_valid_from = None

            # Wenn Standort- und Stadtlimit gleich sind, bleiben wir bei Stadtzaehlung.
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

        self._send_json(payload)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/dashboard":
            self._handle_dashboard()
            return
        if path == "/api/bookings":
            self._handle_bookings()
            return
        if path == "/api/stands":
            month = parse_qs(parsed.query).get("month", [None])[0]
            self._handle_stands(month)
            return
        if path == "/api/meta":
            self._handle_meta()
            return

        if path == "/" or path == "/index.html":
            self._send_file(UI_ROOT / "index.html", "text/html; charset=utf-8")
            return
        if path == "/styles.css":
            self._send_file(UI_ROOT / "styles.css", "text/css; charset=utf-8")
            return
        if path == "/app.js":
            self._send_file(UI_ROOT / "app.js", "application/javascript; charset=utf-8")
            return

        self.send_error(404, "Not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path == "/api/bookings":
                self._handle_create_booking()
                return
            if path == "/api/stands":
                self._handle_create_stand()
                return
            self.send_error(404, "Not found")
        except Exception as error:
            self._send_json({"error": str(error)}, status=400)

    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path.startswith("/api/bookings/"):
                booking_id = int(path.split("/")[-1])
                self._handle_update_booking(booking_id)
                return
            if path.startswith("/api/stands/"):
                location_id = int(path.split("/")[-1])
                self._handle_update_stand(location_id)
                return
            self.send_error(404, "Not found")
        except Exception as error:
            self._send_json({"error": str(error)}, status=400)


def run_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    server = HTTPServer((host, port), RequestHandler)
    print(f"Server running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    run_server(args.host, args.port)
