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

const maxCountMsgInChat = 30;
let p = "";
let nav = '';
let br = ''
let ID = 1;
let countOfMsgMoreThanConst = 0;


socket.on('receive_msg', function(username, msg) {
  nav = document.createElement('nav')
  nav.innerHTML = username + get_current_time();
  nav.id = ID;

  p = document.createElement("p");
  p.innerHTML = msg;
  p.id = ID;

  if (ID > maxCountMsgInChat + 1 || countOfMsgMoreThanConst === 1) {
    if ((countOfMsgMoreThanConst === 1 || countOfMsgMoreThanConst === 0) && ID > maxCountMsgInChat + 1) {
      ID = 1;
      countOfMsgMoreThanConst = 1;
    }
    for (let i = 0; i <= 1; i++) {
      let obj = document.getElementById(`${ID}`);
      obj.remove();
    }
  }

  document.querySelector(".message").appendChild(nav);
  document.querySelector(".message").appendChild(p);
  SmoothScrollTo(`#${ID}`, 100);
  ID++;
})

