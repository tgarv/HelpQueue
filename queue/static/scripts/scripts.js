$(document).ready(function(){
	$("#logout").click(function(){logoutButton()});
	$("#adminLogout").click(function(){adminLogoutButton()});
	var studentID = $(".nameHeader").attr("id");
	console.log(studentID);
	registerUserTicket($(".ticket"+studentID));
});

var logoutButton = function(){
	//Post an AJAX request to log the user out
	$.post($SCRIPT_ROOT + '/logout', {},
		function(data){
			//Once the request has been processed, return to the main page (login page)
			window.location.href = $SCRIPT_ROOT;
		});
}

var adminLogoutButton = function(){
	$.post($SCRIPT_ROOT + '/adminLogout', {},
		function(data){
			//Once the request has been processed, return to the main page (login page)
			window.location.href = $SCRIPT_ROOT;
		});
}

var registerUserTicket = function(ticket){
	ticket.append("<div id='cancelTicketDiv'>Leave Queue</div>");
	$("#cancelTicketDiv").click(function(){
		$.post($SCRIPT_ROOT + '/removeTicket', {ticketID: $(ticket).attr('id')}, 
			function(data){
				console.log(data);
				window.location.href = $SCRIPT_ROOT;
			});
	});
}
