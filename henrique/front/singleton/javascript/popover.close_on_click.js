(function() {
    var scripts = document.getElementsByTagName("script"),
        src = scripts[scripts.length-1].src;



    $(function() {
        var isVisible = false;

        var hideAllPopovers = function() {
           $('[data-toggle="popover"]').each(function() {
                $(this).popover('hide');
            });
        };

        $('[data-toggle="popover"]').popover({
            //html: true,
            trigger: 'manual'
        }).on('click', function(e) {
            // if any other popovers are visible, hide them
            if(isVisible) {
                hideAllPopovers();
            }

            $(this).popover('show');

            // handle clicking on the popover itself
            $('.popover').off('click').on('click', function(e) {
                e.stopPropagation(); // prevent event for bubbling up => will not get caught with document.onclick
            });

            isVisible = true;
            e.stopPropagation();
        });


        $(document).on('click', function(e) {
            hideAllPopovers();
            isVisible = false;
        });
    });

}