$(document).ready(function(){
	$("#logout").click(function(){logoutButton()});

});

var logoutButton = function(){
	$.POST($SCRIPT_ROOT + '/logout', {},
		function(data){
			console.log(data);
		}
});
