select inv_item_sk,inv_warehouse_sk
from inventory where inv_quantity_on_hand > 10
group by inv_item_sk,inv_warehouse_sk
having sum(inv_quantity_on_hand)>20
order by inv_warehouse_sk
limit 100;