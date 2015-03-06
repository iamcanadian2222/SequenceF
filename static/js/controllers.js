/**
 * Created by JLyon on 3/4/2015.
 */
'use strict';

/* Controllers */

var sequenceApp = angular.module('sequenceApp', ['ui.bootstrap']);

sequenceApp.controller('SequenceCtrl', function($scope, $http, $modal, $log, $filter) {
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
    $scope.openAddEdit = function (size, name, sequence, sessionKey) {
        var modalInstance = $modal.open({
          templateUrl: 'templates/add_sequence.html',
          controller: 'ModalAddNewCtrl',
          size: size,
          resolve: {
              sequenceName: function(){ return name; },
              sequence: function(){ return sequence; },
              sessionKey: function(){ return sessionKey }
          }

        });

        modalInstance.result.then(function (map) {
            if(map["isEdit"]){
                var item = $filter('filter')($scope.sequences, {key: map["item"].session_key})[0];
                item.name = map["item"].name;
                item.sequence = map["item"].sequence;
            }
            else {
                $scope.sequences.unshift(map["item"]); //add to the beginning of the array
            }
        }, function () {
          $log.info('Modal dismissed at: ' + new Date());
        });
    };

     $scope.confirmDelete = function (size, record) {
        var modalConfirmInstance = $modal.open({
          templateUrl: 'templates/confirmation.html',
          controller: 'ModalConfirmDeleteCtrl',
          size: size,
          resolve: {
              record: function(){ return record; }
              //sequenceKey: function(){ return sequence_key; }
          }

        });

        modalConfirmInstance.result.then(function (record) {
            var idx = $scope.sequences.indexOf(record); //find the index of the item we just removed
            if(idx >= 0)
                $scope.sequences.splice(idx,1); //and remove it locally
        }, function () {
          $log.info('Modal dismissed at: ' + new Date());
        });
    };

});


// Please note that $modalInstance represents a modal window (instance) dependency.
// It is not the same as the $modal service used above.

sequenceApp.controller('ModalAddNewCtrl', function ($scope, $modalInstance, $http, $log, sequenceName, sequence, sessionKey) {
    $scope.sequence = sequence ? sequence.slice(0) : [,];
    $scope.sequenceName = sequenceName ? sequenceName : "";
    $scope.sessionKey = sessionKey;
    $scope.isEditMode = typeof sessionKey != 'undefined'; //if we were passed a key, we are in edit mode;

    $scope.ok = function () {
        $scope.createSequence();
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.createSequence = function(){
        if($scope.isEditMode) {
            $log.info("Editing item " + sequenceName + " (" + sessionKey + ")");
            var item = {"session_key": $scope.sessionKey,"sequence": $scope.sequence, "name": $scope.sequenceName};
            $http.put("/sequence/" + sessionKey, item)
                .success(function (data, status) {
                    var map = {"isEdit": true, "item": item};
                    $modalInstance.close(map);
                })
                .error(function (data, status) {
                    alert("Oh noes!");
                });
        }else{
            //create a new item if we aren't in edit mode
            $log.info("Creating new item from copy of " + sequenceName);
            $http.post("/sequence", {"sequence": $scope.sequence, "name": $scope.sequenceName})
                .success(function (data, status) {
                    var map = {"isEdit": false, "item": data};
                    $modalInstance.close(map);
                })
                .error(function (data, status) {
                    alert("Oh noes!");
                });
        }
    };

    $scope.addSequenceItem = function() {
        $scope.sequence.push(null);
    };

});

/* -------------- Confirmation Modal (eg. Confirm Delete) ----------------- */
sequenceApp.controller('ModalConfirmDeleteCtrl', function ($scope, $modalInstance, $http, record) {
    $scope.dataRecord = record;
    $scope.sequenceName = record.name ? record.name : "[Unknown]";
    $scope.confirmationMessage = "Are you sure you want to delete the sequence "+ $scope.sequenceName +"?"
    $scope.sequenceKey = record.key;

    $scope.ok = function () {
        $scope.deleteSequence();
    };

    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    $scope.confirm = function(){
        $scope.deleteSequence()
    }

    $scope.deleteSequence = function(){
        $http.delete("/sequence/" + $scope.sequenceKey)
            .success(function(data, status){
                $modalInstance.close($scope.dataRecord);
            })
            .error(function(data, status){
                alert("Oh noes!");
            });
    };

});
