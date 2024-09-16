import mysql from 'mysql2/promise';

const db = mysql.createPool({
  host: 'localhost',
  user: 'root',
  password: 'amyn@08101970',
  database: 'mysqltosheet',
});

export default db;



