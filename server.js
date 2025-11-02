require('dotenv').config();

// ตอนจะใช้ ก็เรียกจาก process.env
const apiKey = process.env.PAYMENT_API_KEY;
const dbUrl = process.env.DATABASE_URL;
const port = process.env.PORT;