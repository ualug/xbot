String.prototype.enlolcrypt = function (cipher) {
  cipher = cipher || "aeoiubcdfghjklmnpqrstvwxyz";
  return this.split("").map(function (T) {
    var c = /[A-Z]/.test(T), T = T.toLowerCase(), i = cipher.indexOf(T);
    if (/[^a-z]/.test(T)) { return T; }

    if ((new RegExp("["+cipher.substr(0,5)+"]")).test(T)) {
      T = cipher[(i+2)%5];
    } else {
      T = cipher[(i+5)%21+5];
    }

    return c?T.toUpperCase():T;
  }).join("");
}

String.prototype.delolcrypt = function (cipher) {
  cipher = cipher || "aeoiubcdfghjklmnpqrstvwxyz";
  return this.split("").map(function (T) {
    var c = /[A-Z]/.test(T), T = T.toLowerCase(), i = cipher.indexOf(T),
        mod = function(a,n) {return ((a%n)+n)%n;};
    if (/[^a-z]/.test(T)) { return T; }

    if ((new RegExp("["+cipher.substr(0,5)+"]")).test(T)) {
      T = cipher[mod(i-2,5)];
    } else {
      T = cipher[mod(i-15,21)+5];
    }

    return c?T.toUpperCase():T;
  }).join("");
}