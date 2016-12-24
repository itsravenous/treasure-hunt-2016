function showError(message) {
  document.forms[0].setAttribute('hidden', true);
  document.body.parentNode.className = '';
  setTimeout(function() {
    var msg = document.createElement('p');
    msg.className = 'message';
    msg.innerHTML = message;
    msg.setAttribute('hidden', true);
    document.forms[0].parentNode.insertBefore(msg, document.forms[0]);
    msg.removeAttribute('hidden');
  }, 500);
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
      var button = document.querySelector('button[value='+value+']');
      var buttons = document.forms[0].getElementsByTagName('button');
      for(var i = 0; i < buttons.length; i++) {
        buttons[i].setAttribute('disabled', true);
      }
      button.className += ' claimed';
      button.innerHTML = 'Claimed by ' + value.split('').join('.').toUpperCase();

      if (gameover) {
        setTimeout(function() {
          showError('Final cube recovered!  Now find the other competing agents and deliver this message.  Your performance assessments are ready.  Please review them carefully.');
        }, 500);
      }
    } else {
      // We reached our target server, but it returned an error

      if (result.error = 1) {
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
