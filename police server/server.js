'use strict'
const express = require('express');
const backend = express();
const server = require('http').createServer(backend).listen(3000);
server.keepAliveTimeout=5555;
const socketio = require('socket.io')(server);
const path = require('path') 
const serve_static = require('serve-static') // To access files
const session = require('express-session');

// Configuration for clients
backend.use(express.json()) // Support json
backend.use(express.urlencoded({extended:true})) // Receive extended methods to encode URL
backend.use('/public', serve_static(path.join(__dirname, 'public'))) // Setting so that /public directory can be used
backend.use('/node_modules/socket.io/client-dist', express.static(__dirname+'/node_modules/socket.io/client-dist')) // socket.io

// Session setting
backend.use(session({
    //httpOnly: true, // Session information cannot be used through javascript
    //secure: true,	// Session information can only be exchanged in https only
    secret: 'secret key', // Key for encryption
    resave: false,
    saveUninitialized: true,
}));

// configuration of get request
backend.get("/", (req, res) => {
    res.redirect('/public/Login.html')
})
backend.get("/Observation", (req, res) => {
    if(req.session.user){ // If logged in
        authorized_ips.push(req.ip);
        res.sendFile(__dirname+'/staff_only/Observation.html');
        console.log(req.session.user)
    }
    else
        res.send("<script>alert('Invalid access'); location.href='/public/Login.html';</script>");
});

let authorized_ips=[];
let user_ID = 'police'; let user_PW = '112';
// Set what to do when a post request from '/process/login' arrives
backend.post('/process/login', (request, response)=>{
    const param_ID = request.body.id;
    const param_PW = request.body.password;
    
    if(param_ID == user_ID && param_PW == user_PW){ // Login successful
        if(!request.session.user){
            request.session.user = {
                id: param_ID,
                authorized: true
            };
        }
        console.log('('+request.ip+') logged in');
      
        response.send("<script>alert('Login successful'); location.href='/Observation';</script>");
        response.end();
    }
    else{ // Login failed
        response.send("<script>alert('Login failed'); location.href='/public/Login.html';</script>");
        response.end();
    }
});

// backend.post("/process/message from python", (req, res) => { // Request from python
//     console.log(req.body);
//     socketio.emit('message from python', req.body.message);
// })

socketio.on("connection", (socket)=>{
    if(authorized_ips.findIndex((element)=>{return element==socket.conn.remoteAddress})!=-1){ // Authentification
        socket.join("observation room");
        console.log("("+socket.conn.remoteAddress+") connected to the socket room");
    }

    socket.on("disconnect", (reason)=>{ // Remove disconnected users from authorized_ips
        authorized_ips.splice(authorized_ips.findIndex((element)=>{element==socket.conn.remoteAddress}), 1)
        console.log("("+socket.conn.remoteAddress+") disconnected from the socket room");
    })

	socket.on('frame from python', (image_as_text) => {
		socketio.in("observation room").emit('image as text', image_as_text);
	});
    socket.on('message from python', (message) => {
		//console.log(message);
		socketio.in("observation room").emit('message from python', message);
	});
});