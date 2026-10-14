--!script
delete from {{catalog}}.audit.audit;
delete from {{catalog}}.audit.table;  
delete from {{catalog}}.audit.test; 
delete from {{catalog}}.audit.version;
