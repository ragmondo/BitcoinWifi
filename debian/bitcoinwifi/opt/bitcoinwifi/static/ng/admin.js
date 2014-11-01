'use strict';

angular.module('app', ['app.home','app.filters', 'app.directives', 'app.controllers', 'ngRoute'])
.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/home', {templateUrl: 'static/partials/home.html',controller: 'CtrlHome'});
  $routeProvider.when('/stat', {templateUrl: 'static/partials/stat.html',controller: 'CtrlStat'});
  $routeProvider.when('/conf', {templateUrl: 'static/partials/conf.html',controller: 'CtrlConf'});

  $routeProvider.otherwise({redirectTo: '/home'});
}]);