from __future__ import annotations

from app.intents.types import IntentType
from app.routes.base import BaseRoute


class RouteFactory:
    def __init__(self, route_map: dict[IntentType, BaseRoute]) -> None:
        self.route_map = route_map

    def get_route(self, intent: IntentType) -> BaseRoute:
        route = self.route_map.get(intent)
        if route is None:
            raise ValueError(f"No route registered for intent={intent}")
        return route
