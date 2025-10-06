/**
 * EJEMPLO: Código Node.js con Anti-patrones
 * Este código funciona pero tiene múltiples problemas de performance y seguridad
 */

const fs = require('fs');
const crypto = require('crypto');
const express = require('express');
const mysql = require('mysql');

const app = express();

// ❌ CRITICAL: Variable global sin límite
const globalCache = {};

// ❌ HIGH: Event listener sin cleanup
const EventEmitter = require('events');
const emitter = new EventEmitter();
emitter.on('data', (data) => {
  console.log(data);
  // Este listener nunca se remueve
});

// ❌ CRITICAL: Operación síncrona que bloquea event loop
app.get('/users', (req, res) => {
  const data = fs.readFileSync('./data/users.json', 'utf8');  // 🔴 BLOCKING
  const users = JSON.parse(data);
  res.json(users);
});

// ❌ CRITICAL: Crypto síncrono bloquea 500ms
app.post('/hash-password', (req, res) => {
  const hash = crypto.pbkdf2Sync(  // 🔴 Bloquea event loop
    req.body.password,
    'salt',
    100000,
    64,
    'sha512'
  );
  res.json({ hash: hash.toString('hex') });
});

// ❌ CRITICAL: N+1 Query Problem
app.get('/users-with-orders', async (req, res) => {
  const users = await User.findAll();  // 1 query
  
  for (const user of users) {  // 🔴 N queries
    const orders = await Order.findAll({ where: { userId: user.id } });
    user.orders = orders;
  }
  
  res.json(users);
});

// ❌ CRITICAL: Promise sin .catch() - unhandled rejection
app.get('/user/:id', (req, res) => {
  fetchUser(req.params.id)
    .then(user => res.json(user));  // 🔴 Sin error handling
  // Si falla, crash en producción
});

// ❌ CRITICAL: SQL Injection vulnerability
app.get('/search', (req, res) => {
  const query = "SELECT * FROM users WHERE name = '" + req.query.name + "'";  // 🔴 SQL Injection
  connection.query(query, (err, results) => {
    res.json(results);
  });
});

// ❌ CRITICAL: eval() - code injection
app.post('/calculate', (req, res) => {
  const result = eval(req.body.expression);  // 🔴 NUNCA USAR EVAL
  res.json({ result });
});

// ❌ CRITICAL: No connection pooling
app.get('/db-query', (req, res) => {
  const connection = mysql.createConnection({  // 🔴 Nueva conexión cada vez
    host: 'localhost',
    user: 'root',
    database: 'mydb'
  });
  
  connection.query('SELECT * FROM users', (err, results) => {
    connection.end();
    res.json(results);
  });
});

// ❌ HIGH: setInterval sin clearInterval
app.get('/start-polling', (req, res) => {
  setInterval(() => {  // 🔴 Memory leak
    pollDatabase();
  }, 1000);
  res.send('Polling started');
});

// ❌ HIGH: Callback hell
app.get('/nested-data/:id', (req, res) => {
  getUser(req.params.id, (err, user) => {  // 🔴 Callback hell
    if (err) return res.status(500).send(err);
    
    getOrders(user.id, (err, orders) => {
      if (err) return res.status(500).send(err);
      
      getOrderDetails(orders[0].id, (err, details) => {
        if (err) return res.status(500).send(err);
        
        res.json({ user, orders, details });
      });
    });
  });
});

// ❌ HIGH: Leer archivo grande sin streams
app.get('/download/large-file', (req, res) => {
  const data = fs.readFileSync('./data/large-file.csv');  // 🔴 1GB en memoria
  res.send(data);
});

// ❌ HIGH: Regex compilation en loop
app.post('/validate-emails', (req, res) => {
  const emails = req.body.emails;
  const valid = [];
  
  for (const email of emails) {
    if (email.match(/^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$/)) {  // 🔴 Compila regex cada vez
      valid.push(email);
    }
  }
  
  res.json(valid);
});

// ❌ MEDIUM: Variables de entorno sin validación
const API_KEY = process.env.API_KEY;  // 🔴 Puede ser undefined
const PORT = process.env.PORT;

// ❌ MEDIUM: JSON.parse en grandes payloads
app.post('/process-large-json', (req, res) => {
  const largeData = JSON.parse(req.body.data);  // 🔴 Bloquea si >10MB
  processData(largeData);
  res.send('OK');
});

// ❌ MEDIUM: try/catch sin finally (resource leak)
app.get('/read-file', async (req, res) => {
  try {
    const file = await openFile('./data.txt');
    const content = await file.read();
    res.send(content);
  } catch (err) {
    res.status(500).send(err);
  }
  // 🔴 file nunca se cierra si hay error
});

// ❌ CRITICAL: Empty catch (swallowing errors)
app.get('/silent-errors', async (req, res) => {
  try {
    await riskyOperation();
    res.send('OK');
  } catch (err) {
    // 🔴 Error ignorado completamente
  }
});

// ❌ MEDIUM: Object allocation en loop
app.post('/process-items', (req, res) => {
  const results = [];
  
  for (let i = 0; i < 10000; i++) {
    const obj = {  // 🔴 Nueva allocation cada iteración
      id: i,
      data: processItem(i)
    };
    results.push(obj);
  }
  
  res.json(results);
});

// ❌ MEDIUM: Buffer.concat en loop
app.post('/combine-buffers', (req, res) => {
  let combined = Buffer.alloc(0);
  
  for (const chunk of req.body.chunks) {
    combined = Buffer.concat([combined, chunk]);  // 🔴 O(N²) performance
  }
  
  res.send(combined);
});

// ❌ LOW: async sin await
async function unnecessaryAsync() {  // 🔴 async innecesario
  return "Hello";
  // No hay await en ningún lado
}

// ❌ MEDIUM: SELECT * en lugar de columnas específicas
app.get('/all-users', (req, res) => {
  connection.query('SELECT * FROM users', (err, results) => {  // 🔴 Trae todas las columnas
    res.json(results);
  });
});

// Helper functions
function pollDatabase() { /* ... */ }
function processItem(i) { return i * 2; }
function processData(data) { /* ... */ }
function getUser(id, cb) { cb(null, {}); }
function getOrders(userId, cb) { cb(null, []); }
function getOrderDetails(orderId, cb) { cb(null, {}); }
function fetchUser(id) { return Promise.resolve({}); }
function openFile(path) { return Promise.resolve({ read: () => '' }); }
function riskyOperation() { return Promise.resolve(); }

class User {
  static async findAll() { return []; }
}

class Order {
  static async findAll(opts) { return []; }
}

const connection = {
  query: (sql, cb) => cb(null, [])
};

app.listen(PORT || 3000);

module.exports = app;