'use strict';

/* Controllers */

angular.module('app.home', [])

.controller('CtrlHome', function($scope,$timeout) {
  $scope.z=0;

  $scope.zCheck = function(){
    $scope.move();
  }

  $scope.move = function(){
    $scope.z+=5;
    if($scope.z<100)
    $timeout($scope.move, Math.floor(Math.random() * 500));
  }
})