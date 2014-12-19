$(function() {
    var max = 0;
    $('label').each(function() {
        if ($(this).width() > max) {
            max = $(this).width();
            max = max + 5;
        }
    });
    $('label').width(max);
});

