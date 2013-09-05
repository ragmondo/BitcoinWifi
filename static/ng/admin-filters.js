'use strict';

/* Filters */

angular.module('app.filters', [])
.filter('duration', function() {
  return function(s) {
    if(!s) return 'loading';
    var d=Math.floor(s%60)+'s';
    if(s < 60){return d;} s/=60; d=Math.floor(s%60)+'m '+d;
    if(s < 60){return d;} s/=60; d=Math.floor(s%60)+'h '+d;
    if(s < 24){return d;} s/=24; d=Math.floor(s%24)+'d '+d;
    return d;
  }
});