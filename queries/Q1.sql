select avg(ss_quantity), avg(ss_net_profit) from store_sales,catalog_sales where cs_bill_customer_sk = ss_customer_sk and ss_quantity > 10 and 
ss_net_profit > 0
limit 100;
