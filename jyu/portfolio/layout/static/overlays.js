/*globals jQuery,common_content_filter,kukit*/
jQuery(function($) {
  var init = function(el) {
    try {
      // autocomplete-plugin must be inited before placeholder-plugin
      $(el).find("form div[id$=autocomplete]").autocomplete_z3cform();
      $(el).find("form .field").placeholder_z3cform();
    } catch (err) {
      // Plugins above may not exist on all systems :)
   };
    // Init KSS, but remember that KSS is made optional in 4.1!
    $(el).find("form").one("focus", function() {
      kukit.engine.setupEvents();
    });
  };
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
    }).bind("onClose", function() {
    });
  });
});