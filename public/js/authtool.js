$(document).ready(function() {
  $('#userinfo-popover').popover();
  $('.form-link').click(function(e) {
    e.preventDefault();
    var linkId = $(this).attr('id');
    $('.form-link').removeClass('active');
    var formId = linkId.substring(0, linkId.length-5);
    $('.index-form').fadeOut(100);
    $('#' + formId).delay(100).fadeIn(100);
    $(this).addClass('active');
  });
  $('#forgot-form-well-link').click(function(e) {
    e.preventDefault();
    $("#forgot-form-link").trigger('click');
  });
  $("#login-form").submit(function(e) {
    e.preventDefault();
    var postdata = {username: $("#login-username").val(), password: $("#password").val()};
    $.post("/login", postdata, function(data) {
      var errmsg = data.error || " Unknown error. Contact your Systems Administrator."
      if (data.ok == true) {
        window.location.assign("/update");
      } else {
        $("#alert_placeholder").html(
          '<div class="alert alert-danger alert-dismissable">' +
          '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' +
          '<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span> ' +
          '<span class="sr-only">Error:</span>' +
          errmsg +
          '</div>'
        );
      }
    });
  });
  $("#forgot-form").submit(function(e) {
    e.preventDefault();
    var postdata = {
      emailaddr: $("#forgot-username").val(),
      email_type: 'password'
    };
    $.post("/forgot", postdata, function(data) {
      $("#alert_placeholder").html(
        '<div class="alert alert-success alert-dismissable">' +
        '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' +
        '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span> ' +
        '<span class="sr-only">Success!</span>' +
        'Password reset email has been sent.' +
        '</div>'
      );
    });
  });
  $("#forgotuname-form").submit(function(e) {
    e.preventDefault();
    var postdata = {
      emailaddr: $("#forgotuname-username").val(),
      email_type: 'username'
    };
    $.post("/forgot", postdata, function(data) {
      $("#alert_placeholder").html(
        '<div class="alert alert-success alert-dismissable">' +
        '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' +
        '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span> ' +
        '<span class="sr-only">Success!</span>' +
        'Your username has been emailed to you.' +
        '</div>'
      );
      setTimeout(function() { 
        $(".alert").alert('close'); 
      }, 2000);
      $("#login-form-link").trigger('click');
    });
  });
  $("#reset-form").validator().on('submit', (function(e) {
    if (!e.isDefaultPrevented()) {
      var postdata = {newpassword: $("#newpassword").val()};
      $.post("/change", postdata, function(data) {
        $("#newpassword").val('');
        $("#confirmPassword").val('');
        if (data.ok == true) {
          $("#alert_placeholder").html(
            '<div class="alert alert-success alert-dismissable">' +
            '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' +
            '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span> ' +
            '<span class="sr-only">Success!</span>' +
            'Password has been reset.' +
            '</div>'
          );
          $("#reset-panel").fadeOut(1000);
          setTimeout(function() {
            window.location.assign("/");
          }, 3000);
        } else {
          $("#alert_placeholder").html(
            '<div class="alert alert-danger alert-dismissable">' +
            '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' +
            '<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span> ' +
            '<span class="sr-only">Error:</span>' +
            data.error +
            '</div>'
          );
        }
      });
    };
    e.preventDefault();
  }));
  $("#change-form").validator().on('submit', (function(e) {
    if (!e.isDefaultPrevented()) {
      var postdata = {
        oldpassword: $("#oldpassword").val(), 
        newpassword: $("#newpassword").val(),
      };
      $.post("/change", postdata, function(data) {
        $("#oldpassword").val('');
        $("#newpassword").val('');
        $("#confirmPassword").val('');
        var errmsg = data.error || 'Unable to change password.'
        if (data.ok == true) {
          $("#alert_placeholder").html(
            '<div class="alert alert-success alert-dismissable">' +
            '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' +
            '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span> ' +
            '<span class="sr-only">Success!</span>' +
            'Password has been reset.' +
            '</div>'
          );
        } else {
          $("#alert_placeholder").html(
            '<div class="alert alert-danger alert-dismissable">' +
            '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' +
            '<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span> ' +
            '<span class="sr-only">Error:</span>' +
            errmsg +
            '</div>'
          );
          return;
        };
      });
    };
    e.preventDefault();
  }));
  $("#addkey-form").validator().on('submit', (function(e) {
    if (!e.isDefaultPrevented()) {
      var postdata = {sshpubkey: $("#publickey").val()};
      $.post("/sshkey", postdata, function(data) {
        var errmsg = data.error || 'Unable to add key.'
        $("#publickey").val('');
        $("#addkeymodal").modal('hide');
        if (data.ok == false) {
          $("#alert_placeholder").html(
            '<div class="alert alert-danger alert-dismissable">' +
            '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' +
            '<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span> ' +
            '<span class="sr-only">Error:</span>' +
            errmsg +
            '</div>'
          );
          return;
        };
        $("#sshpubkeys").append(
          '<li class="list-group-item">' +
          '<form role="form" id="key-' + data.fingerprint.replace(/:/g, '-') + '">' +
          '<input type="hidden" name="key-fprint" value="' + data.fingerprint + '">' +
          '<button type="submit" name="delete-submit" class="btn btn-xs btn-danger pull-right">' +
          '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>' +
          '</button>' +
          '<h5 class="list-group-item-heading">' + data.comment + '</h5>' +
          '<code class="list-group-item-key">' + data.fingerprint + '</code>' +
          '</form>' +
          '</li>'
        );
      });
    };
    e.preventDefault();
  }));
  // handle ssh key fields 
  $("#sshpubkeys").on('submit', "form[id^='key']",  (function(e, type) {
    e.preventDefault();
    var keyItem = this;
    var params = {sshpubkey: $(this).closest('form').find("input[name=key-fprint]").val()};
    var urlquery = $.param(params);
    BootstrapDialog.show({
      type: 'type-danger',
      size: 'size-small',
      title: 'Confirm delete',
      message: 'Are you sure you want to delete this key?',
      buttons: [{
        label: 'Delete',
        cssClass: 'btn-danger',
        action: function(dialogRef){
          dialogRef.close();
          $.ajax({
            url: '/sshkey?' + urlquery,
            type: 'DELETE',
            success: function(data) {
              var errmsg = data.error || 'Unable to delete key.'
              if (data.ok == false) {
                $("#alert_placeholder").html(
                  '<div class="alert alert-danger alert-dismissable">' +
                  '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>' +
                  '<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span> ' +
                  '<span class="sr-only">Error:</span>' +
                  errmsg +
                  '</div>'
                );
              } else {
                $(keyItem).parent().fadeOut('slow');
              }
            }
          });
        }
      }]
    });
  }));
 
});
