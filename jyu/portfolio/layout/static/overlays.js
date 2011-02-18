/*globals jQuery,common_content_filter,kukit*/
jQuery(function($) {
  var init = function(el) {
    $(el).find("#content-core form").one("focus", function() {
      // plugins below may not exist on all setups
      try { $(this).find("div[id$=autocomplete]").autocomplete_z3cform(); } catch (err) {};
      // autocomplete-plugin must be inited before placeholder-plugin
      try { $(this).find(".field").placeholder_z3cform(); } catch (err) {};
      // markdown
      try { $(this).find("input[value='text/x-web-markdown']")
            .parent().find("textarea").markdown_z3cform(); } catch (err) {};
      // Init KSS, but remember that KSS is made optional in 4.1!
      kukit.engine.setupEvents();
    });
  };
  // Init overlay forms for tiles
  $('#remind-contentmenu-tiles li a, '
    +'a.tile-edit, a.tile-delete').each(function() {
    $($(this).prepOverlay({
      subtype: 'ajax',
      cssclass: 'content',
      filter: common_content_filter,
      formselector: 'form[id!="ok"]',
      closeselector: '#buttons-cancel',
      noform: function() {
        return 'reload';
      },
      afterpost: function(el) {
        $(el).find("#content-core form").one("focus", function() {
          if ($.fn.ploneTabInit) {
            $(el).ploneTabInit();
          }
        });
        init(el);
      }
    }).attr("rel")).bind("onLoad", function() {
      init(this);
    });
  });
});