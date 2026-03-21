from __future__ import annotations

import base64
from datetime import datetime
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import joinedload, sessionmaker

from config import Config
from models import Base, Coord, Pereval, PerevalImage, User

PROTECTED_USER_FIELDS = ("fam", "name", "otc", "email", "phone")
LEVEL_TO_MODEL = {
    "winter": "winter_level",
    "summer": "summer_level",
    "autumn": "autumn_level",
    "spring": "spring_level",
}
ROOT_UPDATE_FIELDS = ("beautyTitle", "title", "other_titles", "connect")


class Database:
    """Класс для работы с БД."""

    def __init__(self, db_url: str | None = None) -> None:
        db_url = db_url or Config.get_db_url()
        engine_kwargs: dict[str, Any] = {}
        if db_url.startswith("sqlite"):
            engine_kwargs["connect_args"] = {"check_same_thread": False}

        self.engine = create_engine(db_url, **engine_kwargs)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    @staticmethod
    def _normalize_compare_value(value: Any) -> str:
        if value is None:
            return ""
        return str(value).strip()

    @staticmethod
    def _parse_add_time(value: Any) -> datetime:
        if not value:
            return datetime.utcnow()
        if isinstance(value, datetime):
            return value

        normalized = str(value).strip().replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(normalized)
        except ValueError:
            return datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _decode_image_data(raw_data: str) -> bytes:
        if not raw_data:
            return b""

        payload = raw_data
        if isinstance(raw_data, str) and raw_data.startswith("data:") and "," in raw_data:
            payload = raw_data.split(",", 1)[1]

        return base64.b64decode(payload)

    @staticmethod
    def _serialize_image(image: PerevalImage) -> dict[str, Any]:
        return {
            "id": image.id,
            "title": image.title,
            "data": base64.b64encode(image.img).decode("utf-8") if image.img else None,
            "date_added": image.date_added.isoformat(sep=" "),
        }

    def serialize_pereval(self, pereval: Pereval) -> dict[str, Any]:
        return {
            "id": pereval.id,
            "beautyTitle": pereval.beautyTitle,
            "title": pereval.title,
            "other_titles": pereval.other_titles,
            "connect": pereval.connect,
            "add_time": pereval.add_time.isoformat(sep=" "),
            "status": pereval.status,
            "user": {
                "email": pereval.user.email,
                "phone": pereval.user.phone,
                "fam": pereval.user.fam,
                "name": pereval.user.name,
                "otc": pereval.user.otc,
            },
            "coords": {
                "latitude": pereval.coord.latitude,
                "longitude": pereval.coord.longitude,
                "height": pereval.coord.height,
            },
            "level": {
                "winter": pereval.winter_level,
                "summer": pereval.summer_level,
                "autumn": pereval.autumn_level,
                "spring": pereval.spring_level,
            },
            "images": [self._serialize_image(image) for image in pereval.images],
        }

    def add_pereval(self, data: dict[str, Any]) -> tuple[int | None, str | None]:
        """Добавляет пользователя, координаты, перевал и изображения."""
        session = self.Session()
        try:
            user_data = data["user"]
            user = session.query(User).filter_by(email=user_data["email"]).first()
            if not user:
                user = User(
                    email=user_data["email"],
                    phone=user_data.get("phone"),
                    fam=user_data.get("fam"),
                    name=user_data.get("name"),
                    otc=user_data.get("otc"),
                )
                session.add(user)
                session.flush()

            coords_data = data["coords"]
            coord = Coord(
                latitude=float(coords_data["latitude"]),
                longitude=float(coords_data["longitude"]),
                height=int(coords_data["height"]),
            )
            session.add(coord)
            session.flush()

            level = data.get("level", {})
            pereval = Pereval(
                beautyTitle=data.get("beautyTitle"),
                title=data.get("title"),
                other_titles=data.get("other_titles"),
                connect=data.get("connect"),
                add_time=self._parse_add_time(data.get("add_time")),
                user_id=user.id,
                coord_id=coord.id,
                winter_level=level.get("winter"),
                summer_level=level.get("summer"),
                autumn_level=level.get("autumn"),
                spring_level=level.get("spring"),
                status="new",
            )
            session.add(pereval)
            session.flush()

            for image in data.get("images", []):
                raw_data = image.get("data")
                if not raw_data:
                    continue

                image_bytes = self._decode_image_data(raw_data)
                pereval_image = PerevalImage(
                    pereval_id=pereval.id,
                    title=image.get("title"),
                    img=image_bytes,
                )
                session.add(pereval_image)

            session.commit()
            return pereval.id, None
        except Exception as exc:  # noqa: BLE001
            session.rollback()
            return None, str(exc)
        finally:
            session.close()

    def get_pereval(self, pereval_id: int) -> dict[str, Any] | None:
        session = self.Session()
        try:
            pereval = (
                session.query(Pereval)
                .options(joinedload(Pereval.user), joinedload(Pereval.coord), joinedload(Pereval.images))
                .filter(Pereval.id == pereval_id)
                .first()
            )
            if not pereval:
                return None
            return self.serialize_pereval(pereval)
        finally:
            session.close()

    def get_perevals_by_email(self, email: str) -> list[dict[str, Any]]:
        session = self.Session()
        try:
            perevals = (
                session.query(Pereval)
                .join(User)
                .options(joinedload(Pereval.user), joinedload(Pereval.coord), joinedload(Pereval.images))
                .filter(User.email == email)
                .order_by(Pereval.id.asc())
                .all()
            )
            return [self.serialize_pereval(pereval) for pereval in perevals]
        finally:
            session.close()

    def set_status(self, pereval_id: int, status: str) -> bool:
        """Вспомогательный метод для тестов и ручной проверки бизнес-логики."""
        session = self.Session()
        try:
            pereval = session.query(Pereval).filter(Pereval.id == pereval_id).first()
            if not pereval:
                return False
            pereval.status = status
            session.commit()
            return True
        finally:
            session.close()

    def update_pereval(self, pereval_id: int, data: dict[str, Any]) -> tuple[bool, str]:
        session = self.Session()
        try:
            pereval = (
                session.query(Pereval)
                .options(joinedload(Pereval.user), joinedload(Pereval.coord), joinedload(Pereval.images))
                .filter(Pereval.id == pereval_id)
                .first()
            )
            if not pereval:
                return False, "Pereval with the specified id was not found"

            if pereval.status != "new":
                return False, f"Pereval can only be edited in status 'new'. Current status: {pereval.status}"

            if not isinstance(data, dict):
                return False, "Invalid JSON body"

            user_data = data.get("user")
            if user_data is not None:
                if not isinstance(user_data, dict):
                    return False, "Invalid field: user must be an object"

                for field in PROTECTED_USER_FIELDS:
                    if field not in user_data:
                        continue
                    current_value = self._normalize_compare_value(getattr(pereval.user, field))
                    incoming_value = self._normalize_compare_value(user_data.get(field))
                    if incoming_value != current_value:
                        return False, f"Protected user field cannot be changed: {field}"

            for field in ROOT_UPDATE_FIELDS:
                if field in data:
                    setattr(pereval, field, data.get(field))

            if "add_time" in data:
                pereval.add_time = self._parse_add_time(data.get("add_time"))

            coords_data = data.get("coords")
            if coords_data is not None:
                if not isinstance(coords_data, dict):
                    return False, "Invalid field: coords must be an object"

                if "latitude" in coords_data:
                    pereval.coord.latitude = float(coords_data["latitude"])
                if "longitude" in coords_data:
                    pereval.coord.longitude = float(coords_data["longitude"])
                if "height" in coords_data:
                    pereval.coord.height = int(coords_data["height"])

            level_data = data.get("level")
            if level_data is not None:
                if not isinstance(level_data, dict):
                    return False, "Invalid field: level must be an object"

                for api_key, model_attr in LEVEL_TO_MODEL.items():
                    if api_key in level_data:
                        setattr(pereval, model_attr, level_data.get(api_key))

            if "images" in data:
                images_data = data.get("images") or []
                if not isinstance(images_data, list):
                    return False, "Invalid field: images must be a list"

                for image in list(pereval.images):
                    session.delete(image)
                session.flush()

                for image in images_data:
                    raw_data = image.get("data")
                    if not raw_data:
                        continue
                    image_bytes = self._decode_image_data(raw_data)
                    session.add(
                        PerevalImage(
                            pereval_id=pereval.id,
                            title=image.get("title"),
                            img=image_bytes,
                        )
                    )

            session.commit()
            return True, "The record was updated successfully"
        except Exception as exc:  # noqa: BLE001
            session.rollback()
            return False, str(exc)
        finally:
            session.close()
