from __future__ import annotations

import re
from typing import Any

from flask import Flask, jsonify, request
from flasgger import Swagger
from werkzeug.middleware.proxy_fix import ProxyFix

from database import Database

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "Pereval REST API",
        "description": (
            "API для учебного проекта ФСТР: добавление, просмотр, редактирование "
            "и фильтрация перевалов по email пользователя."
        ),
        "version": "1.0.0",
    },
    "basePath": "/",
    "schemes": ["https"],
}


def validate_input(data: dict[str, Any]) -> tuple[bool, str]:
    """Проверяет обязательные поля и базовый формат входных данных."""
    required_fields = ["beautyTitle", "title", "user", "coords", "level"]
    for field in required_fields:
        if field not in data:
            return False, f"Missing field: {field}"

    user = data.get("user", {})
    if not isinstance(user, dict):
        return False, "Invalid field: user must be an object"

    email = user.get("email")
    if not email or not EMAIL_RE.match(str(email)):
        return False, "Invalid or missing email"

    coords = data.get("coords", {})
    if not isinstance(coords, dict):
        return False, "Invalid field: coords must be an object"

    try:
        float(coords["latitude"])
        float(coords["longitude"])
        int(coords["height"])
    except (KeyError, TypeError, ValueError):
        return False, "Invalid coordinates (missing or non-numeric)"

    level = data.get("level", {})
    if not isinstance(level, dict):
        return False, "Invalid field: level must be an object"

    images = data.get("images", [])
    if images is not None and not isinstance(images, list):
        return False, "Invalid field: images must be a list"

    return True, ""


def create_app(database_instance: Database | None = None) -> Flask:
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.url_map.strict_slashes = False
    Swagger(app, template=SWAGGER_TEMPLATE)

    db = database_instance or Database()

    @app.get("/health")
    def healthcheck():
        """Служебный эндпоинт для проверки доступности приложения.
        ---
        tags:
          - Service
        responses:
          200:
            description: Приложение работает
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: ok
        """
        return jsonify({"status": "ok"}), 200
    
    @app.get("/")
    def index():
      return jsonify(
        {
            "message": "Pereval REST API is running",
            "health": "/health",
            "docs": "/apidocs/",
        }
    ), 200

    @app.post("/submitData")
    def submit_data():
        """Добавить новый перевал.
        ---
        tags:
          - Pereval
        consumes:
          - application/json
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required:
                - beautyTitle
                - title
                - user
                - coords
                - level
              properties:
                beautyTitle:
                  type: string
                  example: пер.
                title:
                  type: string
                  example: Пхия
                other_titles:
                  type: string
                  example: Триев
                connect:
                  type: string
                  example: ''
                add_time:
                  type: string
                  example: '2024-01-01 12:00:00'
                user:
                  type: object
                  properties:
                    email:
                      type: string
                      example: user@example.com
                    phone:
                      type: string
                      example: '+79990001122'
                    fam:
                      type: string
                      example: Иванов
                    name:
                      type: string
                      example: Иван
                    otc:
                      type: string
                      example: Иванович
                coords:
                  type: object
                  properties:
                    latitude:
                      type: number
                      example: 45.3842
                    longitude:
                      type: number
                      example: 7.1525
                    height:
                      type: integer
                      example: 1200
                level:
                  type: object
                  properties:
                    winter:
                      type: string
                    summer:
                      type: string
                    autumn:
                      type: string
                    spring:
                      type: string
                images:
                  type: array
                  items:
                    type: object
                    properties:
                      title:
                        type: string
                        example: Вид на перевал
                      data:
                        type: string
                        example: iVBORw0KGgoAAAANSUhEUgAAAAUA
        responses:
          200:
            description: Перевал успешно добавлен
          400:
            description: Ошибка валидации входных данных
          500:
            description: Ошибка сервера или БД
        """
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"status": 400, "message": "No JSON provided"}), 400

        valid, message = validate_input(data)
        if not valid:
            return jsonify({"status": 400, "message": message}), 400

        pereval_id, error = db.add_pereval(data)
        if error:
            return jsonify({"status": 500, "message": error}), 500

        return jsonify({"status": 200, "id": pereval_id, "message": "Success"}), 200

    @app.get("/submitData")
    def get_user_perevals():
        """Получить список перевалов по email пользователя.
        ---
        tags:
          - Pereval
        parameters:
          - in: query
            name: user__email
            type: string
            required: true
            description: Email пользователя
        responses:
          200:
            description: Список перевалов пользователя
          400:
            description: Некорректный или отсутствующий email
        """
        user_email = request.args.get("user__email")
        if not user_email:
            return jsonify({"message": "Query parameter user__email is required"}), 400

        if not EMAIL_RE.match(user_email):
            return jsonify({"message": "Invalid email format"}), 400

        return jsonify(db.get_perevals_by_email(user_email)), 200

    @app.get("/submitData/<int:pereval_id>")
    def get_pereval(pereval_id: int):
        """Получить перевал по id.
        ---
        tags:
          - Pereval
        parameters:
          - in: path
            name: pereval_id
            type: integer
            required: true
            description: Идентификатор перевала
        responses:
          200:
            description: Перевал найден
          404:
            description: Перевал не найден
        """
        pereval = db.get_pereval(pereval_id)
        if not pereval:
            return jsonify({"message": "Pereval not found"}), 404
        return jsonify(pereval), 200

    @app.patch("/submitData/<int:pereval_id>")
    def patch_pereval(pereval_id: int):
        """Обновить данные перевала по id.
        ---
        tags:
          - Pereval
        consumes:
          - application/json
        parameters:
          - in: path
            name: pereval_id
            type: integer
            required: true
            description: Идентификатор перевала
          - in: body
            name: body
            required: true
            schema:
              type: object
              description: |
                Частичное обновление разрешено только для записей со статусом new.
                Поля пользователя (fam, name, otc, email, phone) изменять нельзя.
        responses:
          200:
            description: Результат обновления
        """
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"state": 0, "message": "No JSON provided"}), 200

        success, message = db.update_pereval(pereval_id, data)
        if success:
            return jsonify({"state": 1, "message": message}), 200
        return jsonify({"state": 0, "message": message}), 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
