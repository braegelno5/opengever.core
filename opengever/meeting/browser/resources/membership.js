(function(global, $) {

  "use strict";

  var init = function() {

    var start = $("<input class='spv-datetime-widget' type='text' />");
    var end = $("<input class='spv-datetime-widget' type='text' />");

    start.insertAfter("#formfield-form-widgets-date_from > label");
    end.insertAfter("#formfield-form-widgets-date_to > label");

    start = new global.Datetimepicker({ target: start, startView: 2, minView: 2, time: false });
    end = new global.Datetimepicker({ target: end, startView: 2, minView: 2, time: false });

    var range = new global.Rangetimepicker({ start: start, end: end, minRange: 24 });

    var applyPloneWidget = function() {
      $("#formfield-form-widgets-date_from").attr("value", start.element.val());
      $("#formfield-form-widgets-date_to").attr("value", end.element.val());
    };

    start.on("changeDate", applyPloneWidget);
    end.on("changeDate", applyPloneWidget);
  };

  $(function() {
    if($(".template-add-membership").length) {
      init();
    }
  });

}(window, jQuery));
