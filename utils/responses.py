"""
utils/responses.py — Standardised JSON response helpers.
"""

from flask import jsonify
from typing import Any, Optional


def success(data: Any, message: str = "ok", status: int = 200):
    return jsonify({"success": True, "message": message, "data": data}), status


def error(message: str, status: int = 400, details: Optional[Any] = None):
    payload = {"success": False, "message": message}
    if details is not None:
        payload["details"] = details
    return jsonify(payload), status
