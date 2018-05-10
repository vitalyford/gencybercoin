$(function() {
  $(document).on('change', ':file', function() {
    var input    = $(this),
        numFiles = input.get(0).files ? input.get(0).files.length : 1,
        label    = input.val().replace(/\\/g, '/').replace(/.*\//, '');
    input.trigger('selectedfile', [numFiles, label]);
  });
  $(document).ready( function() {
      $(':file').on('selectedfile', function(event, numFiles, label) {
          var input = $(this).parents('.input-group').find(':text');
          if (input.length) {
              input.val(label);
          }
      });
  });
});

// Only enable the go-to-the-top button when the document has a long scroll bar
if ( ($(window).height() + 100) < $(document).height() ) {
    $('#top-link-block').removeClass('hidden').affix({
        // how far to scroll down before link "slides" into view
        offset: {top:100}
    });
}
