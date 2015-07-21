select avg(ws_ext_sales_price), avg(ws_ext_wholesale_cost)
from web_sales
where web_sales.ws_sales_price between 100.00 and 150.00
group by ws_web_site_sk;