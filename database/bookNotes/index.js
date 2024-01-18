const express = require('express');
const bodyParser = require('body-parser');
const pg = require('pg');
const app = express();
const port = 3000;

// Set up PostgreSQL connection
const pool = new pg.Pool({
  user: 'your_postgres_user',
  host: 'localhost',
  database: 'your_database_name',
  password: 'your_database_password',
  port: 5432,
});

app.use(bodyParser.urlencoded({ extended: true }));
app.set('view engine', 'ejs');

// Example route to render the home page
app.get('/', async (req, res) => {
  try {
    const client = await pool.connect();
    const result = await client.query('SELECT * FROM books');
    const books = result.rows;
    res.render('index', { books });
    client.release();
  } catch (err) {
    console.error(err);
    res.status(500).send('Internal Server Error');
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
