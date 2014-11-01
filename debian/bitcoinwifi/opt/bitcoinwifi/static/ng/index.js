'use strict';

/* Controllers */

angular.module('app', ['app.home'])

.controller('Main', function($scope,$http) {
  $http.get('/status').then(function(d){
    if(d.data){
      angular.forEach(d.data.data, function(v,k) {$scope[k]=v;});
    }
  });
})