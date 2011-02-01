/*globals jQuery,common_content_filter,kukit*/
jQuery(function($) {
  var init = function(el) {
    // plugins below may not exist on all setups
    try { $(el).find("form div[id$=autocomplete]").autocomplete_z3cform(); } catch (err) {};
    // autocomplete-plugin must be inited before placeholder-plugin
    try { $(el).find("form .field").placeholder_z3cform(); } catch (err) {};
    // Init KSS, but remember that KSS is made optional in 4.1!
    $(el).find("form").one("focus", function() {
      kukit.engine.setupEvents();
    });
  };
  // Init overlay forms for tiles
  $('a.tile-add, a.tile-edit, a.tile-delete').each(function() {
    $($(this).prepOverlay({
      subtype: 'ajax',
      cssclass: 'content',
      width: '40em',
      filter: common_content_filter,
      formselector: 'form[id!="ok"]',
      closeselector: '#buttons-cancel',
      noform: function() {
        return 'reload';
      },
      afterpost: function(el) {
        init(el);
      }
    }).attr("rel")).bind("onLoad", function() {
      init(this);
    });
  });
});