"""Application constants."""


class Roles:
    ADMIN = "admin"
    CUSTOMER = "customer"
    AGENT = "agent"

    ALL = {ADMIN, CUSTOMER, AGENT}


class ShipmentStatus:
    CREATED = "created"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

    ACTIVE = {CREATED, IN_TRANSIT, OUT_FOR_DELIVERY}
    ALL = {CREATED, IN_TRANSIT, OUT_FOR_DELIVERY, DELIVERED, CANCELLED}
    AGENT_ALLOWED = {IN_TRANSIT, OUT_FOR_DELIVERY, DELIVERED}


TRACKING_PREFIX = "TRK"
