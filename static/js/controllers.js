/**
 * Created by JLyon on 3/4/2015.
 */
'use strict';

/* Controllers */

var phonecatApp = angular.module('sequenceApp', []);

phonecatApp.controller('SequenceCtrl', function($scope, $http) {
    $http.get("/sequence").success(function(data, status){
        $scope.sequences = data;
    })
});