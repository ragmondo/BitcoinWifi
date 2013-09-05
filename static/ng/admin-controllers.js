'use strict';

/* Controllers */

angular.module('app.controllers', [])

.controller('Main', function($scope,$http) {
  // Alerts
  Alertify.log.delay=10000;

  // Fetch status
  $scope.status = function() {
    $http.get('/status').then(function(d){
      if(d.data.info){
        angular.forEach(d.data.info, function(v,k) {Alertify.log.create(v.type, v.text);});
      }
      if(d.data.data){
        angular.forEach(d.data.data, function(v,k) {$scope[k]=v;});
      }
    });
  }

  $scope.status();
})

.controller('CtrlConf', function($scope,$http) {
  // Sync config
  $scope.sync = function(data,method,alert) {
    $http({method:method?'POST':'GET', url:'/sync', data:$scope[data]}).success(function(d){
      if(d.data.info && alert){
        angular.forEach(d.data.info, function(v,k) {Alertify.log.create(v.type, v.text);});
      }
      if(d.data.data){
        angular.forEach(d.data.data, function(v,k) {$scope[k]=v;});
      }
      if(alert){
        Alertify.log.success("Sync "+d);
      }
    })
    .error(function(){
      if(alert){
        Alertify.log.error("Sync "+data);
      }
    })
    .then(
      function(d){
        if(alert){
          Alertify.log.info("Response length: "+angular.toJson(d).length);
        }
      },
      function(d){
        if(alert){
          Alertify.log.info("Response length: "+angular.toJson(d).length);
        }
      }
    );
  }
})



.controller('CtrlStat', function($scope,$http) {
  $scope.bitcoinaddress="test";
  // Sync settings
  // Note: not possible to remove settings!
  $scope.status = function() {
    $http.get('/status').then(function(d){
      console.log(d)
      if(d.info){
        angular.forEach(d.info, function(v,k) {Alertify.log.create(v.type, v.text);});
      }
      if(d.data){
        angular.forEach(d.data, function(v,k) {$scope[k]=v;});
      }
    });
  }

  $scope.status();
})

