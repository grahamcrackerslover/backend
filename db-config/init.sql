ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'root';
FLUSH PRIVILEGES;

CREATE DATABASE IF NOT EXISTS backend_db;
