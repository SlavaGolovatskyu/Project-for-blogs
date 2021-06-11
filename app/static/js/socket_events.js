const socket = io();

document.querySelector(".send__msg").addEventListener('keyup', function(e) {
  if (e.keyCode === 13) {
    if (this.value.trim() === "") {
      return false;
    }
    socket.emit('send_message', {'msg': this.value.trim()});
    this.value = "";
  }
});

socket.on('get_online', function(online) {
  document.querySelector('.online').innerHTML = `Онлайн на сайте: ${online}`;
})

const maxMsgOnPage = 30;
let p = "";
let nav = '';
let br = ''
let idForElement = 1;
let countCircleMsg = 0;


socket.on('take_msg', function(username, msg) {
  nav = document.createElement('nav')
  nav.innerHTML = username + get_current_time();
  nav.id = idForElement;
  p = document.createElement("p");
  p.innerHTML = msg;
  p.id = idForElement;
  br = document.createElement("br");
  br.id = idForElement;
  if (idForElement > maxMsgOnPage + 1 || countCircleMsg === 1) {
    if ((countCircleMsg === 1 || countCircleMsg === 0) && idForElement > maxMsgOnPage + 1) {
      idForElement = 1;
      countCircleMsg = 1;
    }
    for (let i = 0; i <= 2; i++) {
      let obj = document.getElementById(`${idForElement}`);
      obj.remove();
    }
  }
  document.querySelector(".message").appendChild(nav);
  document.querySelector(".message").appendChild(p);
  document.querySelector(".message").appendChild(br);
  SmoothScrollTo(`#${idForElement}`, 100);
  idForElement++;
})

