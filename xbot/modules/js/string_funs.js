String.prototype.jumble = (function () {
  return this.split(" ").map(function (T) {
    return T.substring(0, 1) + (T.length > 2 ? T.split("").slice(1, T.length - 1).sort(function () {
      return Math.round(Math.random()) - 0.5;
    }).join("") : "") + (T.length > 1 ? T.substring(T.length - 1) : "");
  }).join(" ");
});

String.prototype.repeat = (function (n) {
  var s = "";
  for (var i = 0; i < n; i++) {
    s += this;
  }
  return s;
});

String.prototype.reverse = (function (del) {
  del = del || "";
  return this.split(del).reverse().join(del);
});