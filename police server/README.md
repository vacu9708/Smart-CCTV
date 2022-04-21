# node.js police office server

### ID: police / password: 112 입력<br>
![image](https://user-images.githubusercontent.com/67142421/162588624-778981c8-9409-4353-a065-5b67aaf44668.png)

### Prevetion of access without authentification(using HTTP session)
![image](https://user-images.githubusercontent.com/67142421/162632552-dd4392b5-7a5d-44c5-ab5f-11cef86d1977.png)

### Login failure<br>
![image](https://user-images.githubusercontent.com/67142421/162588639-ae8b17ed-29af-461c-b71a-f717d5bfe712.png)

### Login successful<br>
![image](https://user-images.githubusercontent.com/67142421/162588709-9ba21214-f09e-4c55-ae35-ead172aaaa55.png)
![image](https://user-images.githubusercontent.com/67142421/162632571-cba7e7bb-9ede-4bc7-a0cb-e368b9640632.png)

## Send signal from python to police
node.js
~~~javascript
backend.post("/process/detection", (req, res) => { // Request from python
    console.log(req.body);
    socket.emit('message from python', req.body.message);
});
~~~
python
~~~Python
import requests

data = {"message": "From python: Detected"}
requests.post('http://127.0.0.1:3000/process/detection', json=data)
~~~
![image](https://user-images.githubusercontent.com/67142421/162632613-34163610-53b2-446a-b94b-1f65bc0b89b4.png)
