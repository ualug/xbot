String.prototype.color = function(fg,bg) {
  var conv = function(thing, _default) {
    if (+thing < 16 && +thing > -1) { return +thing; }
    thing = "white black blue green red brown purple orange yellow lime teal cyan royal pink grey silver".split(" ").indexOf(thing);
    if (thing != -1) { return thing; }
    return _default;
  };
  
  
  fg = conv(fg, 2);
  bg = conv(bg, "");
  bg = bg && ","+bg;
  
  return "\x03" + fg + bg + this + "\x0F";
};

String.prototype.colour = String.prototype.color;

String.prototype.highlight = function () {
  return this.color("black", "yellow");
};