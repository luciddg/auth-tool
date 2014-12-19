var modal = (function(){
  var 
  method = {},
  $overlay,
  $modal,
  $modalcontent,
  $close;

  method.center = function() {
    var top, left;

    top = Math.max($(window).height() - $modal.outerHeight(), 0) / 2;
    left = Math.max($(window).width() - $modal.outerWidth(), 0) / 2;

    $modal.css({
      top:top + $(window).scrollTop(),
      left:left + $(window).scrollLeft(),
    });
  };

  method.open = function (settings) {
    $modalcontent.empty().append(settings.modalcontent);

    $modal.css({
      width: settings.width || 'auto',
      height: settings.height || 'auto',
    });

    method.center();

    $(window).bind('resize.modal', method.center);
    
    $modal.show();
    $overlay.show();

    $modal.submit(function(e) {
      var formObj = $(e.target);
      var postData = formObj.serializeArray();
      $('#error').hide();
      $('#success').hide();
      $.post('/addkey', postData, function(data) {
          if (data.match(/^error/)) {
              $('#error').html(data);
              $('#error').show();
          } else {
              $('#success').html(data);
              $('#success').show();
              location.reload();
          }
      });
      event.preventDefault();
      method.close();
    });

  };

  method.close = function () {
    $modal.hide();
    $overlay.hide();
    $modalcontent.empty();
    $(window).unbind('resize.modal');
  };

  $overlay = $('<div id="overlay" />');
  $modal = $('<div id="modal"></div>');
  $modalcontent = $('<div id = "modalcontent" />');
  $close = $('<a href="#" id="close">x</a>');

  $modal.hide();
  $overlay.hide();
  $modal.append($modalcontent, $close);

  $(document).ready(function(){
    $('div[id^="modalForm"]').hide();
    $('body').append($overlay, $modal);  

    $('#modalPop').submit(function() {
      event.preventDefault();
      modal.open({modalcontent: $('div[id^="modalForm"]').html()});
    });

  });

  $close.click(function(e){
    e.preventDefault();
    method.close();
  });

  return method;
}());

