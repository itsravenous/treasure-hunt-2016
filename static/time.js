// TODO
function showError(message) {
  //document.body.textContent = message;
  alert(message);
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
    result = JSON.parse(this.response);

    if (this.status >= 200 && this.status < 400) {
      // Success!
      var scores = result.score;
      var gameover = result.game_over;

      // TODO
      // (Seriously.
      //  Frontend will benefit significantly from some feedback
      //  to show that the button has been pressed).
      showError(JSON.stringify(result));
    } else {
      // We reached our target server, but it returned an error

      if (result.error = 1) {
        // This line is okay, but showError() is still TODO
        showError('This cube has already been claimed.');
      } else {
        unexpectedError();
        console.log(result);
      }
    }
  };

  request.onerror = function() {
    // There was a connection error of some sort
    networkError();
  };

  request.send();
}
