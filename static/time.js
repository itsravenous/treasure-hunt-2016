document.addEventListener('DOMContentLoaded', function() {
  console.log('load')
  document.forms[0].addEventListener('submit', function(e) {
    e.preventDefault();
    return false;
  });
  document.forms[0].addEventListener('click', function(e) {
    var el = e.target || e.srcElement;
    if(el.nodeName.toLowerCase() === 'button') {
      claim(el.name, el.value);
    }
  });
});

function claim(name, value) {
  var url = document.forms[0].action + '?' + name + '=' + value;
  var request = new XMLHttpRequest();
  request.open('POST', url, true);
  request.onload = function() {
    if (this.status >= 200 && this.status < 400) {
      // Success!
      this.response;
    } else {
      // We reached our target server, but it returned an error

    }
  };

  request.onerror = function() {
    // There was a connection error of some sort
  };

  request.send();
}
