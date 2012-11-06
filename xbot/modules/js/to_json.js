Object.prototype.to_json = Object.prototype.toString = function () {
  return JSON.stringify(this);
};