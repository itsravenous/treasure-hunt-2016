// TODO
function showError(message) {
  document.body.textContent = message;
}
function unexpectedError() {
  showError('Sorry, there was an error in this application.');
}
function networkError() {
  showError('Failed to connect to server.  Check your network connection.  Are you using the right WiFi network?');
}

window.addEventListener('error', function() {
  // Javascript exception (or maybe javascript syntax error)
  unexpectedError();
});
// We have no detection of asset load errors


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
      result = JSON.parse(this.response);

      // TODO
      // (Seriously.
      //  Frontend will benefit significantly from some feedback
      //  to show that the button has been pressed).
      showError(JSON.stringify(result));
    } else {
      // We reached our target server, but it returned an error

      // TODO
      // This was under-specified.
      // It should have been JSON, with a specific error code.
      // It's OK to treat JSON as text, for right now though.
      showError(this.response);
    }
  };

  request.onerror = function() {
    // There was a connection error of some sort
    networkError();
  };

  request.send();
}
