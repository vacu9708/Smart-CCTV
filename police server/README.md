# node.js 경찰서 서버

### 아이디: police / 비밀번호: 112 입력<br>
![image](https://user-images.githubusercontent.com/67142421/162588624-778981c8-9409-4353-a065-5b67aaf44668.png)

### 경찰 전용 페이지에 로그인없이 접근(HTTP session을 이용해서 허가되지않은 접근 방지)
![image](https://user-images.githubusercontent.com/67142421/162632552-dd4392b5-7a5d-44c5-ab5f-11cef86d1977.png)

### 로그인 실패<br>
![image](https://user-images.githubusercontent.com/67142421/162588639-ae8b17ed-29af-461c-b71a-f717d5bfe712.png)

### 로그인 성공 -> 경찰로서 감시 시작<br>
![image](https://user-images.githubusercontent.com/67142421/162588709-9ba21214-f09e-4c55-ae35-ead172aaaa55.png)
![image](https://user-images.githubusercontent.com/67142421/162632571-cba7e7bb-9ede-4bc7-a0cb-e368b9640632.png)

## Python에서 HTTP post요청을 보내면 socket통신으로 경찰 페이지에 신호를 전달
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
