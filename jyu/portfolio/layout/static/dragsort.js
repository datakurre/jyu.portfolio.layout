/*globals jQuery,common_content_filter*/
jQuery(function($) {
  $("#content-core .cell").dragsort({
    itemSelector: '.cell > div',
    dragSelector: 'div',
    dragBetween: true,
    placeHolderTemplate: '<div class="placeholder"></div>',
    dragEnd: function(e) {
      $.get('@@move-tile', {
        tile: $(this).attr("id"),
        target: $(this).parent().attr("id"),
        position: $(this).data("itemidx")
      });
    }
  });
});
