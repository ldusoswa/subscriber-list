import express from 'express';
import bodyParser from 'body-parser';
import fetch from 'node-fetch';

const app = express();
const port = 3000;

app.use(bodyParser.urlencoded({ extended: true }));
app.set('view engine', 'ejs');
app.use(express.static('public'));

let messages = [];

app.get('/', (req, res) => {
    res.render('index', { messages });
});

app.post('/submit', (req, res) => {
    const { winner, prizeName, prizeValue } = req.body;
    const message = {
        winner,
        prizeName,
        prizeValue,
        timestamp: new Date().toISOString()
    };
    messages.unshift(message);
    if (messages.length > 100) {
        messages.pop();
    }
    res.redirect('/');
});

app.get('/notifications', async (req, res) => {
    try {
        const notifications = await getNotifications();
        res.json({ messages: notifications });
    } catch (error) {
        res.status(500).send('Cannot get notifications');
    }
});

const getNotifications = async (amount = 100) => {
    try {
        const response = await fetch('http://localhost:3000/notifications');
        const data = await response.json();
        return data.messages;
    } catch (error) {
        throw new Error('Cannot get notifications');
    }
};

app.listen(port, () => {
    console.log(`App listening at http://localhost:${port}`);
});
