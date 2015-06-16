select a.aq from
(select cs_item_sk, avg(cs_quantity) as aq
from catalog_sales
where cs_quantity > 2
group by cs_item_sk) a join
(select i_item_sk,i_current_price
from item
where i_current_price > 2
order by i_current_price) b
on a.cs_item_sk = b.i_item_sk
order by a.aq
limit 100;