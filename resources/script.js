var num = max = count = 0;
var imgs = [];
var timeoutId = 0;
var clicked = false;
function adjust(opt_num) {
  clearTimeout(timeoutId);
  if (opt_num === num || opt_num < 0 || opt_num >= max) {
    return;
  }
  if (opt_num === 0 || opt_num) {
    num = opt_num;
  }
  var tabs = document.getElementsByClassName('tab');
  var imageHolder = $('.imageholder')[0];
  imageHolder.style['-webkit-transform'] = 'translateX(-'+(num * 100 / max)+'%)';
  imageHolder.style['transform'] = 'translateX(-'+(num * 100 / max)+'%)';
  tabs[0].style.visibility = (num === 0) ? 'hidden' : 'visible';
  tabs[1].style.visibility = (num === max-1) ? 'hidden' : 'visible';
 $('.maintext').children().css('display', 'none');
 $('.maintext :nth-child('+(num+1)+')').css('display', 'inline-block');
  if (window.location.href.match(/listings/)) {
    addThumbnails();
  }
  if (!clicked) {
    timeoutId = setTimeout(function(){ adjust((num + 1) % max) }, 5000); 
  }
};

function addThumbnails() {
  $("#thumbnails").empty();
  var img = imgs[num];
  var imageSrc = img.slice(0,-5);
  var tryToAdd = function(i) {
    var tmp = document.createElement('img');
    var img = new Image();
    img.src = imageSrc + i + '.jpg';
    tmp.src = '/r/images/bgtile.jpg';
    $("#thumbnails").append(tmp);
    tmp.onclick = function(){ changePic(i, tmp.src); };
    img.onload = function(){ $(tmp).addClass(i === 1 ? 'selectedimg' : 'unselectedimg'); tmp.src = img.src; }
    img.onerror = function(){ $(tmp).remove(); };
  };
  for (var i = 1; i <= 3; ++i) {
    tryToAdd(i);
  }
}

function changePic(count, url) {
  $('#thumbnails > img').removeClass('selectedimg').addClass('unselectedimg');
  $('#thumbnails :nth-child('+count+')').removeClass('unselectedimg').addClass('selectedimg');
  var img = $('.imageholder :nth-child('+(num+1)+')');
  img.attr('src', url);
}

var Swiper = function(img) {
  this.x = -1;
  var tmp = this;
  img.addEventListener('touchstart', function(evt){ tmp.down(evt.touches[0]); })
  img.addEventListener('touchend', function(evt){ tmp.up(evt.touches[0]); })
  img.addEventListener('mousedown', function(evt){ tmp.down(evt); })
  img.addEventListener('mouseup', function(evt){ tmp.up(evt); })
};

Swiper.prototype.down = function(evt) {
  this.x = evt.pageX;
};

Swiper.prototype.up = function(evt) {
  var diff = this.x - evt.pageX;
  if (Math.abs(diff) > 10) {
    adjust(num + 1*(diff > 0) - 1*(diff < 0))
  }
  this.x = -1;
};


window.onload = function() {
  var tabs = document.getElementsByClassName('tab');
  var imageholder = document.getElementsByClassName('imageholder')[0];
  if (!imageholder || !tabs.length) return;
  max = imageholder.children.length;
  imageholder.style.width = (max*100) + "%";
  tabs[0].addEventListener('click', function() {
    clicked = true; num=((num-1+max) % max); adjust(); 
  });
  tabs[1].addEventListener('click', function() {
    clicked = true; num=((num+1) % max); adjust();
  });
  if (window.location.href.match(/listings/)) {
    imgs = $.map($('.imageholder > img'), function(e, i){ return e.src });
    var swiper = new Swiper(document.getElementsByClassName('images')[0]);
  }
  adjust();
};
