"""
Business logic regarding the delivery of shipments.
"""

__author__ = "Justin B. (justin@justin.directory)"


from datetime import datetime, timedelta
from random import choice
from uuid import UUID
from app.inventory.warehouse import get_warehouse, get_warehouse_chunks
from app.shipping.models import CreateDeliveryRequest, DeliveryTimeResponse, Shipment, ShipmentDeliveryBreakdown, ShipmentItem
from .enums import SLA, Provider
from .providers import ShipmentProvider, fedex, internal, ups, usps


shipping_providers: dict[Provider, ShipmentProvider] = {
    Provider.FEDEX: fedex.client,
    Provider.UPS: ups.client,
    Provider.USPS: usps.client,
    Provider.INTERNAL: internal.client
}

sla_times: dict[SLA, timedelta] = {
    SLA.STANDARD: timedelta(days=5),
    SLA.EXPRESS: timedelta(days=2),
    SLA.OVERNIGHT: timedelta(days=1),
    SLA.SAME_DAY: timedelta(hours=12)
}


async def get_delivery_breakdown(recipient_address: str, sla: SLA, items: list[ShipmentItem]) -> ShipmentDeliveryBreakdown:
    """
    Get a delivery breakdown for a specific order.
    """
    # Get the expected delivery time.
    expected_at = datetime.now() + sla_times[sla]
    can_meet_sla = True
    warehouse_chunks = await get_warehouse_chunks(recipient_address, items)
    delivery_times: list[DeliveryTimeResponse] = []

    for chunk in warehouse_chunks:
        warehouse = await get_warehouse(chunk.warehouse_id)
        fastest_provider: Provider | None = None
        fastest_time = timedelta.max

        for provider, client in shipping_providers.items():
            delivery_time = await client.get_delivery_time(
                recipient_address, warehouse.address)

            if delivery_time < fastest_time:
                fastest_time = delivery_time
                fastest_provider = provider

            if delivery_time < sla_times[sla]:
                # If we are within the SLA, we can meet it.
                break

        if fastest_time > sla_times[sla]:
            can_meet_sla = False

        delivery_times.append(DeliveryTimeResponse(
            provider=fastest_provider,
            delivery_time=datetime.now()+fastest_time,
            items=chunk.items,
            warehouse_id=chunk.warehouse_id,
            from_address=warehouse.address
        ))

    return ShipmentDeliveryBreakdown(
        recipient_address=recipient_address,
        expected_at=expected_at,
        can_meet_sla=can_meet_sla,
        delivery_times=delivery_times,
    )


async def create_delivery_shipments(request: CreateDeliveryRequest) -> list[Shipment]:
    """
    Create the delivery orders for the request.
    """
    breakdown = await get_delivery_breakdown(request.recipient_address, request.delivery_sla, request.items)
    if not breakdown.can_meet_sla:
        raise ValueError("Cannot meet SLA")
