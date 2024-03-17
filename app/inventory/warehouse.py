"""
Warehouse related classes and functions.
"""

class Warehouse():
    """
    A warehouse which will contain various items, can be used to create shipments.
    """
    def get_stock(self, upc: int) -> int:
        """
        STUB: Given a single UPC and the stock, return the amount of stock available for a specific UPC.
        """

    def stock_available(self, upcs: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """
        STUB: Given a list of items, returns a list of UPCs for items that it has available.
        """

def get_nearest_warehouse(longitude: float, latitude: float) -> Warehouse:
    """
    STUB: Get the nearest warehouse given the longitude & the latitude.
    """
