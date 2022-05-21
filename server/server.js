'use strict'
const express = require('express')
const server = express();
const http_server = require('http').createServer(server).listen(3000);
const socketio = require('socket.io')(http_server)
const path = require('path') 
const serve_static = require('serve-static') // To access files
const session = require('express-session')

// Configuration for clients
server.use(express.json()) // Support json
server.use(express.urlencoded({extended:true})) // Receive extended methods to encode URL
server.use('/public', serve_static(path.join(__dirname, '/public'))) // Setting so that /public directory can be used
server.use('/staff_only', serve_static(path.join(__dirname, '/staff_only'))) // Setting so that /public directory can be used
server.use('/node_modules/socket.io/client-dist', express.static(__dirname+'/node_modules/socket.io/client-dist')) // socket.io

// Session setting
server.use(session({
    //httpOnly: true, // Session information cannot be used through javascript
    //secure: true,	// Session information can only be exchanged in https only
    secret: 'secret key', // Key for encryption
    resave: false,
    saveUninitialized: true,
}));

// Configurations of requests
server.get("/", (req, res) => {
    res.redirect('/public/Login.html')
})

let authorized_ips=[]; // Hash map will be much better!
server.get("/Observation", (req, res) => {
    if(req.session.user){ // If logged in
        authorized_ips.push(req.ip)
        res.sendFile(__dirname+'/staff_only/Observation.html');
        //console.log('('+req.ip+') logged in to the staff page')
    }
    else
        res.send("<script>alert('Invalid access'); location.href='/public/Login.html';</script>");
    //res.end()
});

let user_ID = 'police'; let user_PW = '112';
// Set what to do when a post request from '/process/login' arrives
server.post('/process/login', (req, res)=>{
    const param_ID = req.body.id;
    const param_PW = req.body.password;
    
    if(param_ID == user_ID && param_PW == user_PW){ // Login successful
        if(!req.session.user){
            req.session.user = {
                id: param_ID,
                authorized: true
            };
        }
        res.send("<script>alert('Login successful'); location.href='/Observation';</script>");
        //process.stdout.write('session : '); console.log(req.session.user);
    }
    else // Login failed
        res.send("<script>alert('Login failed'); location.href='/public/Login.html';</script>");
    res.end();
});

server.post("/process/python_login", (req, res)=>{
    const param_ID = req.body.id;
    const param_PW = req.body.password;

    if(param_ID == user_ID && param_PW == user_PW){ // Login successful
        //console.log('('+req.ip+') logged in from python');
        authorized_ips.push(req.ip);
    }
    else 
        console.log('Login failed')
    res.end()
})

// server.post("/process/message from python", (req, res) => { // Request from python
//     console.log(req.body);
//     socketio.emit('message from python', req.body.message);
// })

socketio.on("connection", (socket)=>{
    if(authorized_ips.findIndex((element)=>{return element==socket.conn.remoteAddress})!=-1){ // If found the ip
        socket.join("observation room");
        console.log("("+socket.conn.remoteAddress+") connected to the socket room");
    }
    else
        socket.disconnect()

    socket.on("disconnect", (reason)=>{ // Remove disconnected users from authorized_ips
        let ip_i=authorized_ips.findIndex((element)=>element==socket.conn.remoteAddress)
        if(ip_i!=-1) // If found the ip
            authorized_ips.splice(ip_i, 1) // Delete the ip of the leaving user
        console.log("("+socket.conn.remoteAddress+") disconnected from the socket room");
    })

	socket.on('frame from python', (image_as_text) => {
		socketio.in("observation room").emit('image as text', image_as_text);
	});
    socket.on('message from python', (message) => {
		//console.log('message: '+message);
		socketio.in("observation room").emit('message from python', message);
	});
});