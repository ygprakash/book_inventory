myapp = angular.module('myapp',['ui.router', 'ngStorage']);

myapp.config(["$stateProvider", "$urlRouterProvider", "$locationProvider",
    function configFn($stateProvider, $urlRouterProvider, $locationProvider) {
    $stateProvider.state('root',{
        url: 'index',
        controller: 'index',
        templateUrl: function (params) {
            params = './index.html';
            return params
        },
        data:{}
    }).state('root.loginCtrl',{
        url: '/login',
        // views:{
            // "@":{
                controller: 'loginCtrl',
                templateUrl: function (params) {
                    params = './login.html';
                    return params;
                // }
            // }
        },
        data:{'user':'','password':'','globaldata':''}
    }).state('root.regCtrl',{
        url: '/register',
        // views:{
        //     "@":{
                controller: 'regCtrl',
                templateUrl: function (params) {
                    params = './register.html';
                    return params;
                }
        //     }
        // }
    }).state('root.viewCtrl',{
        url: '/view',
        // views:{
        //     "@":{
                controller: 'viewCtrl',
                templateUrl: function (params) {
                    params = './view.html';
                    return params;
                }
        //     }
        // }
    }).state('root.devCtrl',{
        url: '/dev',
        controller: 'devCtrl',
        templateUrl: function (params){
            params = './developerview.html';
            return params;
        }
    }).state('root.redirectCtrl',{
        url: '/redirect',
        controller: 'redirectCtrl',
        templateUrl: function (params){
            params = './redirect.html';
            return params;
        }
    });
    $locationProvider.html5Mode(true).hashPrefix('!');
    // $urlRouterProvider.when('/','/index.html');
    // $urlRouterProvider.when('/index.html/register','register.html');
    // $urlRouterProvider.when('/index.html/login','login.html');
    // $urlRouterProvider.when('/index.html/view','view.html');
}]);

myapp.controller('index', ['$scope', '$state', '$localStorage', function ($scope, $state, $localStorage) {
    $scope.transition = $state.$urlRouter.location;
    $scope.clicklogin = function () {
        $state.go($state.transitionTo('root.loginCtrl'))
    };
    $scope.newregistration = function () {
        $state.go($state.transitionTo('root.regCtrl'))
    };

}]);

myapp.controller('loginCtrl',['$scope', '$state', '$localStorage','$http', function ($scope, $state, $localStorage,$http) {
    $scope.transition = $state.$urlRouter.location.split('/').pop();
    $scope.login = function (line1, line2) {
        $state.$current.data['user'] = line1;
        $state.$current.data['password'] = line2;

        $http.get("/userlogin?user=" + $state.$current.data['user'] + "&pwd=" + $state.$current.data['password']).success(function (data, status) {
            $state.globaldata = data;
            $localStorage.globaldata = data;
            if (($state.$current.data['user'] === 'admin')&&(data!=='Unauthorized')){
                $state.go($state.transitionTo('root.viewCtrl'));
            }
            else if(data ==='Unauthorized')
            {
                $state.go($state.transitionTo('root.redirectCtrl'));
            }
            else {
                $state.go($state.transitionTo('root.devCtrl'));
            }
        }).error(function (data, status) {
            console.log(data);
            console.log(status);
        });
    };
    //  if ($state.$current.data['user'] === 'admin')
    //         {$state.go($state.transitionTo('root.viewCtrl'));}
    //         else{swtch();}
    //     var swtch = function () {
    //     $state.go($state.transitionTo('root.devCtrl'));
    // }
}]);

myapp.controller('viewCtrl',['$scope', '$state', '$localStorage','$http', function ($scope, $state, $localStorage,$http) {
    $scope.data = $localStorage.globaldata;
    $scope.del_check = false;
    $scope.val ='';

    $scope.upd = function (line55,line5,line6,line7) {
        var id = line55;
        var author = line5;
        var bname = line6;
        var pubon = line7;
        $http.get("/update?author="+author+"&bname="+bname+"&pubon="+pubon+"&id="+id).success(function (data, status) {
            $state.globaldata = data;
            $localStorage.globaldata = data;
            $state.go($state.transitionTo('root.redirectCtrl'))
        }).error(function (data, status){
           console.log(data);
           console.log(status);
        });
    };
    $scope.del = function (line) {
        var id =line['Book Id'];
        $http.get("/del?id="+id).success(function (data, status) {
            $state.globaldata = data;
            $localStorage.globaldata = data;
            $state.go($state.transitionTo('root.redirectCtrl'));
        }).error(function (data, status){
           console.log(data);
           console.log(status);
        });
    };
        $scope.add = function (line1,line2,line3,line4) {
        var id =line1;
        var author = line2;
        var name = line3;
        var date_published = line4;
        $http.get("/add?id="+id+"&name="+name+"&author="+author+"&date_published="+date_published).success(function (data, status) {
            $state.globaldata = data;
            $localStorage.globaldata = data;
            $state.go($state.transitionTo('root.redirectCtrl'));
        }).error(function (data, status){
           console.log(data);
           console.log(status);
        });
    }
}]);

myapp.controller('devCtrl',['$scope', '$state', '$localStorage','$http', function ($scope, $state, $localStorage,$http) {
    $scope.snip = false;
    $scope.data = $state.globaldata;
    $scope.getdata = function (dat) {
        $http.get("/webdav?file="+dat+"&path="+$state.globaldata.directory).success(function (data, status) {
            $state.codesnip = data;
            $scope.codesnip = data;
            $scope.snip = true;
        })
    }
}]);

myapp.controller('redirectCtrl',['$scope', '$state', '$localStorage','$http', function ($scope, $state, $localStorage,$http) {
    $scope.data =$state.globaldata;
}]);
myapp.controller('regCtrl',['$scope', '$state', '$localStorage','$http', function ($scope, $state, $localStorage,$http) {

    $scope.reg = function(uname,email,password,team){
        $http.post("/register?uname="+uname+"&passw="+password+"&mail="+email+"&team="+team).success(function (data, status){
            $state.globaldata = data;
            $state.go($state.transitionTo('root.redirectCtrl'));
        }).error(function (data,status){
            console.log(data);
            console.log(status);
        });
    };
}]);