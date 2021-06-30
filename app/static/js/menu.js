let menuIsOpen = false;

$('#menu').click(
  function (){
    if (menuIsOpen) {
      $('#main_menu').removeClass('menu__open');
      menuIsOpen = false;
    } else {
      $('#main_menu').addClass('menu__open');
      menuIsOpen = true;
    }
  }
)

$('#main_menu').mouseleave(
  function (){
    $('#main_menu').removeClass('menu__open');
    menuIsOpen = false;
  }
)
