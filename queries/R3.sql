select avg(ss_quantity), avg(ss_net_profit) from store_sales where ss_quantity > 10 and ss_net_profit > 0
limit 100;
