$(document).on('click', '#checkout_url', function(){
  event.preventDefault();
  $.ajax({
    url:window.location.pathname + '/@@officeconnector_checkout_url',
  }).success(function(data) {
    window.location = data;
  });
});

$(document).on('click', '#attach_url', function(){
  event.preventDefault();
  $.ajax({
    url:window.location.pathname + '/@@officeconnector_attach_url',
  }).success(function(data) {
    window.location = data;
  });
});
