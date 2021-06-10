function SmoothScrollTo(id_or_Name, timeline){
  let timelength = timeline || 1000;
  $('html, body').animate({
    scrollTop: $(id_or_Name).offset().top-70
  }, timelength, function(){
    window.location = id_or_Name;
  });
}

const get_current_time = () => {
  let today = new Date();
  let hours = (today.getHours() < 10) ? '0' + today.getHours() : today.getHours();
  let minutes = (today.getMinutes() < 10) ? '0' + today.getMinutes() : today.getMinutes();
  let seconds = (today.getSeconds() < 10) ? '0' + today.getSeconds() : today.getSeconds();
  return '   ' + hours + ":" + minutes + ":" + seconds;
}

