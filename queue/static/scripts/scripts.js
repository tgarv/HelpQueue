$(document).ready(function(){
	$("#logout").click(function(){logoutButton()});
	$("#adminLogout").click(function(){adminLogoutButton()});
	var studentID = $(".nameHeader").attr("id");
	//Recognize a particular ticket as belonging to the currently logged-in student
	registerUserTicket($(".ticket"+studentID));
	//Set up the tickets so the admins can deal with them (help or remove them from the queue)
	registerAdminTickets();
	$(".adminTicketExpand").slideToggle(0);
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

//Adds a link to the ticket belonging to the current user so they can remove it from the queue.
var registerUserTicket = function(ticket){
	ticket.append("<div class='cancelTicketDiv'>Leave Queue</div>");
	$(".cancelTicketDiv").click(function(){
		$.post($SCRIPT_ROOT + '/removeTicket', {ticketID: $(ticket).attr('id')}, 
			function(data){
				console.log(data);
				window.location.href = $SCRIPT_ROOT;
			});
	});
}

var registerAdminTickets = function(){
	$(".adminTicketBody").click(function(click){
		click.stopPropagation();
		console.log("clicked");
		$(this).next().slideToggle();
	});
	$(".adminTicket").each(function(index){
		var elem = $("<div class='cancelTicketDiv'>Remove from queue</div>");
		$(this).append(elem);
		var ticketID = $(this).attr('id');
		elem.click(function(){
			$.post($SCRIPT_ROOT + '/removeTicket', {ticketID: ticketID}, 
			function(data){
				console.log(data);
				window.location.href = $SCRIPT_ROOT;
			});
		});
	});
}
