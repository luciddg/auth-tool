$(function() {

  $("#change_pass").submit(function() {
    $('#error').hide();
    $('#success').hide();
    var postdata = {username: $('#username').val(), token: $('#token').val(), password: $('#password').val(), newpass1: $('#newpass1').val(), newpass2: $('#newpass2').val()};

    $.post('/change_pass', postdata, function(data) {

      var errorData = '<ul>';
      var successData = '<ul>';
      var showErr = 0;
      var showSuccess = 0;

      if (typeof(data) == 'object') {
          $.each(data, function() {
              if (this.match(/^Error/)) {
                  showErr = 1;
                  errorData = errorData + '<li>' + this + '</li>';
              } else {
                  showSuccess = 1;
                  successData = successData + '<li>' + this + '</li>';
              }
          });
          if (showErr==1) {
              errorData = errorData + '</ul>';
              $('#error').html(errorData);
              $('#error').show();
          }
          if (showSuccess=='1') {
              successData = successData + '</ul>';
              $('#success').html(successData);
              $('#success').show();
          }
      } else {
          if (data.match(/^Error/)) {
              $('#error').html(data);
              $('#error').show();
          } else {
              $('#success').html(data);
              $('#success').show();
          }
      }
      $('#password').val('');
      $('#newpass1').val('');
      $('#newpass2').val('');
    });
    return false;
  });
});

