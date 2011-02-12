/*globals jQuery,common_content_filter*/
jQuery(function($) {
  $(".documentEditable #content-core .cell.sortable,"
     + ".documentEditable #content-core .cell > .sortable").dragsort({
    itemSelector: '.sortable > div',
    dragSelector: '> div',
    dragBetween: true,
    placeHolderTemplate: '<div class="tile placeholder"></div>',
    dragSelectorExclude: "input, textarea, a[href], a[href] img, a[href] span",
    dragEnd: function(e) {
      var that = this;
      $.get('@@move-tile', {
        tile: $(this).attr("id"),
        target: $(this).parent().attr("id"),
        position: $(this).attr("data-itemidx")
      });
    }
  });
});
