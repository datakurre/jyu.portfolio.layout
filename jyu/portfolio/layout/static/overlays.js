/**
 * @license 
 * jQuery Tools @VERSION / Overlay Apple effect. 
 * 
 * NO COPYRIGHTS OR LICENSES. DO WHAT YOU LIKE.
 * 
 * http://flowplayer.org/tools/overlay/apple.html
 *
 * Since: July 2009
 * Date: @DATE 
 */
/**
 * Customized for jyu.portfolio.layout aka remind at 2011-05-02
 */
jQuery(function($) {
  // version number
  var t = $.tools.overlay, w = $(window); 

  // extend global configuragion with effect specific defaults
  $.extend(t.conf, { 
    start: { top: null, left: null },
    zIndex: 9999
  });

  // utility function
  function getPosition(el) {
    var p = el.offset();
    return {
      top: p.top + el.height() / 2, 
      left: p.left + el.width() / 2
    }; 
  }

  // load 
  var loadEffect = function(pos, onLoad) {
    var that = this,
        conf = this.getConf(),
        overlay = this.getOverlay(),
        trigger = $("[rel=#" + this.getTrigger().attr("id") + "]"),
        oWidth = overlay.outerWidth({margin:true}),
        oHeight = overlay.outerHeight({margin:true}),
        position = conf.fixed ? "fixed" : "absolute",
        box = overlay.data("box");

    // init growing box
    if(!box) {
      box = $("<div/>");
      box.css({
        border: "none",
        backgroundColor: "#ccc",
        display: "none"
      }).width(oWidth).height(oHeight);
      $("body").append(box);
      overlay.data("box", box);
    }

    // initial top & left
    var itop = conf.start.top || Math.round(w.height() / 2), 
    ileft = conf.start.left || Math.round(w.width() / 2);

    if (trigger) {
      var p = getPosition(trigger);
      itop = p.top;
      ileft = p.left;
    } 

    // put overlay into final position
    if (conf.fixed) {
      itop -= w.scrollTop();
      ileft -= w.scrollLeft();
    } else {
      pos.top += w.scrollTop();
      pos.left += w.scrollLeft();
    }

    // store origin
    overlay.data("boxOrigin", {top: itop, left: ileft});

    // initialize background image and make it visible
    box.css({
      position: 'absolute',
      top: itop,
      left: ileft,
      width: 0,
      height: 0,
      opacity: 0.4,
      zIndex: conf.zIndex
    }).show();

    pos.position = position;
    overlay.css(pos);

    // begin growing
    box.animate({
      top: overlay.css("top"),
      left: overlay.css("left"),
      width: oWidth,
      height: oHeight}, conf.speed, function() {
        // set close button and content over the image
        box.css({opacity: 0});
        overlay.css("zIndex", conf.zIndex+1).show();
        if (that.isOpened()) {
          onLoad.call(); 
        } else {
          overlay.hide();
        }
      }).css("position", position);
  };

  // close
  var closeEffect = function(onClose) {

    // variables
    var conf = this.getConf(),
        overlay = this.getOverlay().hide(), 
        trigger = $("[rel=#" + this.getTrigger().attr("id") + "]"),
        box = overlay.data("box"),
        boxOrigin = overlay.data("boxOrigin"),

        css = { 
          top: conf.start.top, 
          left: conf.start.left, 
          opacity: 0.5,
          width: 0,
          height: 0
        };

    // trigger position
    if (trigger) { $.extend(css, getPosition(trigger)); }

    // box origin
    if (boxOrigin) { $.extend(css, boxOrigin); }

    // change from fixed to absolute position
    if (conf.fixed) {
      box.css({position: 'absolute'})
        .animate({ top: "+=" + w.scrollTop(), left: "+=" + w.scrollLeft()}, 0);
    }

    // shrink box
    box.animate(css, conf.closeSpeed, onClose);
  };

  // add overlay effect
  t.addEffect("remind", loadEffect, closeEffect); 
});

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
      $(this).find("input:visible, select:visible, textarea:visible").first().focus();
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
      config: { effect: "remind" },
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
