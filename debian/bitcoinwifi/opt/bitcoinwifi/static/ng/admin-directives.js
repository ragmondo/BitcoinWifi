'use strict';

/* Directives */

angular.module('app.directives', [])

// Toggles .active based on $location.path()
.directive('menuActive', function($rootScope,$location) {
  return function(scope, element, attrs) {
    $rootScope.$on('$routeChangeStart', function (event, next, current) {
      (element.children()[0].hash === '#'+$location.path()) ? element.addClass('active') : element.removeClass('active');
    });
  }
})