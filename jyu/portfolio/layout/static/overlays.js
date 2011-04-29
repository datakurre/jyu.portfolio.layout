/*globals jQuery,common_content_filter,kukit*/
jQuery(function($) {
  // Configuring overlay forms with jQuery widgets is ugly, but let's
  // hope it's worth it.

  // Define support function to init jQuery-widgets on overlay-forms
  var init = function(el) {
    $(el).find("#content-core form, .pb-ajax > div > form").one("focus", function() {
      // plugins below may not exist on all setups
      try { $(this).find("div[id$=autocomplete]").autocomplete_z3cform(); } catch(e1) {}
      // autocomplete-plugin must be inited before placeholder-plugin
      try { $(this).find(".field").placeholder_z3cform(); } catch(e2) {}
      // markdown
      try { $(this).find("input[value='text/x-web-markdown']")
            .parent().find("textarea").markdown_z3cform(); } catch(e3) {}
      // Init KSS, but remember that KSS is made optional in 4.1!
      kukit.engine.setupEvents();
      return false;
    });
  };

  // Init overlay forms for tiles
  $('#remind-contentmenu-tiles li a, a.tile-configure, a.tile-delete').each(function() {
    $($(this).prepOverlay({
      subtype: 'ajax',
      cssclass: 'content',
      filter: common_content_filter,
      formselector: 'form[id!="ok"]',
      closeselector: '#buttons-cancel, #form-buttons-cancel',
      noform: function() {
        return 'reload';
      },
      beforepost: function(form, arr, options) {
        $('<input type="hidden" name="ajax_load" value="1" />').appendTo(form);
        arr.push({name: "ajax_load", value: "1"});
        return true;
      },
      afterpost: function(el) {
        $(el).find("#content-core form").one("focus", function() {
          var options = {
            yearRange: 'c-5:c+5', firstDay: 1,
            showTrigger: '<button type="button" class="datepick">'
              + '<img src="popup_calendar.png" alt="" />'
              + '</button>'
          };
          try { $(el).find(".date-widget, .datetime-widget")
                .parent().datepick_z3cform(options); } catch(e4) {}
          if ($.fn.ploneTabInit) {
            $(el).ploneTabInit();
          }
          return false;
        });
        init(el);
      }
    }).attr("rel")).bind("onLoad", function() {
      init(this);
      return false;
    });
  });
});
