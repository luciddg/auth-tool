$(function() {

  $("#login").submit(function() {
    $('#error').hide();
    $('#success').hide();
    var postdata = {username: $("#username").val(), password: $("#password").val()};
    $.post('/login', postdata, function(data) {
      if (data.match(/^Error/)){
        $("#error").html(data);
        $("#error").show();
      }
      else {
        var url = "/update?username=" + data;
        window.location=url;
      }
    });
    return false ;
  });

  $("#lost").submit(function() {
    var postdata = {lost_username: $("#lost_username").val()};
    $.post('/lost', postdata, function(data) {
      if (data.match(/^Error/)) {
        $("#error").html(data);
        $("#error").show();
      } else {
        $("#success").html(data);
        $("#success").show();
      }
    });
    return false;
  });

});

