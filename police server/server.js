'use strict'
const express = require('express');
const backend = express();
const server = require('http').createServer(backend);
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
});
backend.get("/Observation", (req, res) => {
    console.log(req.session.user)
    if(req.session.user) // If logged in
        res.sendFile(__dirname+'/staff_only/Observation.html');
    else
        res.send("<script>alert('Invalid access'); location.href='/public/Login.html';</script>");
});

// backend.post("/process/detection", (req, res) => { // Request from python
//     console.log(req.body);
//     socketio.emit('message from python', req.body.message);
// });

let authorized_ips=[];
socketio.on("connection", (socket)=>{
    if(authorized_ips.findIndex((element)=>{return element==socket.conn.remoteAddress})!=-1){
        socket.join("observation room");
        console.log("("+socket.conn.remoteAddress+") connected");
    }
    else
        socket.disconnect();

    socket.on("disconnect", (reason)=>{
        authorized_ips.splice(authorized_ips.findIndex((element)=>{element==socket.conn.remoteAddress}), 1)
    })

	socket.on('streaming', (data) => {
        //console.log(data)
		socketio.in("observation room").emit('streaming', data);
	});
    socket.on('message from python', (message) => {
		console.log(message);
		socketio.in("observation room").emit('message from python', message);
	});
})

let user_ID = 'police'; let user_PW = '112';
// Set what to do when a post request from '/process/login' arrives
backend.post('/process/login', (request, response)=>{
    const param_ID = request.body.id;
    const param_PW = request.body.password;
    
    if(param_ID == user_ID && param_PW == user_PW){ // Login successful
        if(request.session.user == undefined){
            request.session.user = {
                id: param_ID,
                authorized: true
            };
            authorized_ips.push(request.ip);
            //console.log(request.ip);
        }

        response.send("<script>alert('Login successful'); location.href='/Observation';</script>");
        response.end();
    }
    else{ // Login failed
        response.send("<script>alert('Login failed'); location.href='/public/Login.html';</script>");
        response.end();
    }
})

server.listen(3000, ()=>{
    console.log('Listening on port 3000')
})