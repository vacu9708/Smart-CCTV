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
    //httpOnly: true,	//자바스크립트를 통해 세션 쿠키를 사용할 수 없도록 함
    //secure: true,	//https 환경에서만 session 정보를 주고받도록처리
    secret: 'secret key',	// Key for encryption
    resave: false, //세션을 언제나 저장할지 설정함
    saveUninitialized: true, //세션이 저장되기 전 uninitialized 상태로 미리 만들어 저장
}));

socketio.on("connection", (socket)=>{
    socket.join("observation room");

	socket.on('streaming', (data) => {
        //console.log(data)
		socketio.in("observation room").emit('streaming', data);
	});
    socket.on('message from python', (message) => {
		console.log(message);
		socketio.in("observation room").emit('message from python', message);
	});
})

// configuration of get request
backend.get("/", (req, res) => {
    res.redirect('/public/Login.html')
});
backend.get("/Observation", (req, res) => {
    if(req.session.user) // If logged in
        res.sendFile(__dirname+'/staff_only/Observation.html');
    else
        res.send("<script>alert('Invalid access'); location.href='/public/Login.html';</script>");
});

// backend.post("/process/detection", (req, res) => { // Request from python
//     console.log(req.body);
//     socketio.emit('message from python', req.body.message);
// });

let user_ID = 'police'; let user_PW = '112';
// Set what to do when a post request from '/process/login' arrives
backend.post('/process/login', (request, response)=>{
    const param_ID = request.body.id;
    const param_PW = request.body.password;
    
    if(param_ID == user_ID && param_PW == user_PW){ // Login successful
        if(request.session.user == undefined)
            request.session.user = {
                id: param_ID,
                authorized: true
            };

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