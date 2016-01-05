(function(global, $) {

  "use strict";

  $.fn.datetimepicker.dates.de = $.fn.datetimepicker.dates["de-ch"] = {
    days: ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"],
    daysShort: ["Son", "Mon", "Die", "Mit", "Don", "Fre", "Sam", "Son"],
    daysMin: ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"],
    months: ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
    monthsShort: ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"],
    today: "Heute",
    suffix: [],
    meridiem: [],
    weekStart: 1,
    format: "dd.mm.yyyy hh:ii"
  };

  $.fn.datetimepicker.dates.fr = {
    days: ["Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"],
    daysShort: ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
    daysMin: ["D", "L", "Ma", "Me", "J", "V", "S", "D"],
    months: ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"],
    monthsShort: ["Jan", "Fev", "Mar", "Avr", "Mai", "Jui", "Jul", "Aou", "Sep", "Oct", "Nov", "Dec"],
    today: "Aujourd'hui",
    suffix: [],
    meridiem: [],
    weekStart: 1,
    format: "dd.mm.yyyy hh:ii"
  };

  $.fn.datetimepicker.dates.it = {
    days: ["Domenica", "Lunedi", "Martedi", "Mercoledi", "Giovedi", "Venerdi", "Sabato", "Domenica"],
    daysShort: ["Dom", "Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"],
    daysMin: ["Do", "Lu", "Ma", "Me", "Gi", "Ve", "Sa", "Do"],
    months: ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"],
    monthsShort: ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"],
    today: "Oggi",
    suffix: [],
    meridiem: [],
    weekStart: 1,
    format: "dd.mm.yyyy hh:ii"
  };

  $.fn.datetimepicker.dates.en = {
    days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    daysShort: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    daysMin: ["Su", "Mop", "Tu", "We", "Th", "Fr", "Sa", "Su"],
    months: ["January", "Febrauary", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    monthsShort: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    today: "Today",
    suffix: [],
    meridiem: [],
    weekStart: 1,
    format: "dd/mm/yyyy hh:ii"
  };

  // Confirmend bug in https://github.com/smalot/bootstrap-datetimepicker/issues/122
  var applyTimezone = function(date) { return new Date(date.setTime(date.getTime() + (date.getTimezoneOffset() * 60 * 1000))); };

  var Datetimepicker = function(options) {

    var lang = $("#ploneLanguage").data("lang");

    options = $.extend({
      target: ".datetimepicker",
      autoclose: true,
      todayHighlight: true,
      todayBtn: true,
      startView: 1,
      minuteStep: 5,
      viewSelect: "year",
      language: lang,
      time: true
    }, options);

    this.element = $(options.target);

    if(!options.time) {
      options.format = $.fn.datetimepicker.dates[lang].format.replace(/[hi:]/gi, "").trim();
    }

    var roundMinutes = function(date, precision) { return new Date(date.setMinutes(Math.ceil(date.getMinutes() / precision) * precision)); };

    var getUTCDate = function(date) { return new Date(date + "UTC"); };

    var convertToLocalTime = function(date) { return applyTimezone(date); };

    this.date = roundMinutes(getUTCDate(new Date()), options.minuteStep);

    this.element.datetimepicker(options);

    this.on = function(event, callback) { this.element.on(event, callback); };

    this.setStartDate = function(date) { this.element.datetimepicker("setStartDate", convertToLocalTime(new Date(date))); };

    this.setEndDate = function(date) { this.element.datetimepicker("setEndDate", convertToLocalTime(new Date(date))); };

    this.setDate = function(date) {
      this.date = new Date(date);
      var localTime = convertToLocalTime(new Date(date));
      this.element.datetimepicker("setDate", localTime);
    };

    this.setDate(this.date);

  };

  Datetimepicker.applyTimezone = applyTimezone;

  global.Datetimepicker = Datetimepicker;

  var Rangetimepicker = function(options) {

    options = $.extend({
      minRange: 1,
      start: {},
      end: {}
    }, options);

    var adjustEndtime = function(start) {
      var end = new Date(new Date(start).setHours(start.getHours() + options.minRange));
      options.end.setDate(end);
    };

    var updateDate = function(date) {
      if(options.minRange && (options.end.date - date) < (options.minRange * 60 * 60 * 1000)) {
        adjustEndtime(date);
      }
      options.end.setStartDate(date);
      options.start.setDate(date);
    };

    updateDate(options.start.date);

    options.start.on("changeDate", function(event) { updateDate(event.date); });
    options.end.on("changeDate", function(event) { options.end.setDate(event.date); });

  };

  global.Rangetimepicker = Rangetimepicker;

}(window, jQuery));
