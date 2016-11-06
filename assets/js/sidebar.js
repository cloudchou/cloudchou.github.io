jQuery(document).ready(function($) {

    $('.level-bar-inner').css('width', '0');

    console.log("document ready")

    $(window).on('load', function() {

        console.log("window ready")

        $('.level-bar-inner').each(function() {

            var itemWidth = $(this).data('level');

            $(this).animate({
                width: itemWidth
            }, 800);



        });

    });



});
