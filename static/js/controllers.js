/**
 * Created by JLyon on 3/4/2015.
 */
'use strict';

/* Controllers */

var sequenceApp = angular.module('sequenceApp', ['ui.bootstrap']);

sequenceApp.controller('SequenceCtrl', function($scope, $http, $modal, $log) {
    $http.get("/sequence").success(function(data, status){
        $scope.sequences = data;
    });

    $scope.addSequence = function() {
        $scope.newSequence.push(null);
    };

    $scope.findLargest = function(session_id, index){
        var url = "/sequence/" + session_id  + "/next-largest/" + index;
        $http.get(url)
            .success(function(data, status){
                alert("The next highest index is: " + data.next_largest_index);
            });
    };


    //-------- Bootstrap modal ---------
    $scope.openAddNew = function (size) {
        var modalInstance = $modal.open({
          templateUrl: 'add_sequence.html',
          controller: 'ModalInstanceCtrl',
          size: size
        });

        modalInstance.result.then(function (newItem) {
            $scope.sequences.push(newItem);
        }, function () {
          $log.info('Modal dismissed at: ' + new Date());
        });
    };

});


// Please note that $modalInstance represents a modal window (instance) dependency.
// It is not the same as the $modal service used above.

sequenceApp.controller('ModalInstanceCtrl', function ($scope, $modalInstance, $http) {
    $scope.newSequence = [,];

    $scope.ok = function () {
        $scope.createSequence();
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.createSequence = function(){
        $http.post("/sequence", {"sequence": $scope.newSequence})
            .success(function(data, status){
                $modalInstance.close(data);
            })
            .error(function(data, status){
                alert("Oh noes!");
            });
    };

    $scope.addSequenceItem = function(){
        $scope.newSequence.push(null);
    };

});
