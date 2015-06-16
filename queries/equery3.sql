set tez.queue.name=queue2;
explain select avg(ss_quantity)
       ,avg(ss_ext_sales_price)
       ,avg(ss_ext_wholesale_cost)
       ,sum(ss_ext_wholesale_cost)
 from store_sales
 where (store_sales.ss_sales_price between 100.00 and 150.00) or (store_sales.ss_net_profit between 100 and 200);
