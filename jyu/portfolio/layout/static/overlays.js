/*globals document,$,jQuery,common_content_filter,kukit*/
$(document).ready(function() {
  var init = function(el) {
    // Init autocomplete must before placeholder:
    try {
      $(el).find("form div[id$=autocomplete]").autocomplete_z3cform();
      $(el).find("form .field").placeholder_z3cform();
    } catch (err) {
    };
    // Init KSS. Remember that KSS is made optional in 4.1!
    $(el).find("form").one("focus", function() {
      kukit.engine.setupEvents();
    });
  };
  $($('a.tile').prepOverlay({
    subtype: 'ajax',
    cssclass: 'content',
    width: '40em',
    filter: common_content_filter,
    formselector: 'form',
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