from sqlalchemy import Column, Integer, String
from services.inventory_service.app.db.base import Base


'''
household model for inventory management caters to both items that are consumed
like air freshners, bulbs which needs to be replaced post their usage and
others like screw drivers, hammers which are durable with a longer life.
The quantity in the model is for bulk items that are purchased in deals 
and stored. Once an item is used, the quantity would drop eventually
making it 0.
Quantity 0 will indicate that is no more items in the storage and needs to 
be replenished. These would majority be items required by all people staying 
in the property.
There is no need for what or who added the item. There are no personal items
added.
e.g: cleaning supplies, kitchen rolls, bulbs, batteries, stationary, tools

Operations
- Add item - will add new household item to the inventory.
- Update item - will update the storage property and the quantity.
- Delete item - will remove the item from the inventory. for incorrectly added item.
- Search Item - will search for an item in the inventory using both general and product name

'''
class Household(Base):
    __tablename__ = "household"
    __table_args__ = {"schema": "inventory", "extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True, nullable=True)
    general_name = Column(String, index=True, nullable=False)
    quantity = Column(Integer, nullable=True)
    storage_id = Column(Integer)
    property_id = Column(Integer, index=True)


'''
Any search made to the household inventory will be logged here only on success.
This is to identify the last user who supposedly searched for the item.
If the item is not in the location, then the last searched user will have to be
asked about its whereabouts. 

TODO: Implement search history logging

'''
# class HouseholdItemSearchDTO(Base):    
#     __tablename__ = "household_search_history"
#     __table_args__ = {"schema": "inventory", "extend_existing": True}

#     search_product: str
#     property_id: int
#     user_id: int