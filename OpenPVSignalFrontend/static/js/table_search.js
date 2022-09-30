$(function(){
    $(".search input").keyup(function () {
        var value = $(this).val().toLowerCase();
    $("#sr_table tbody tr").filter(function() {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
    });
  });
});