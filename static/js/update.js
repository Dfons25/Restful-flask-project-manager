function warn_error(message){
	
		elm = document.getElementById("toggle_opt_div");
		elm.innerHTML = '* ' + message + ' *';
		var newone = elm.cloneNode(true);
		elm.parentNode.replaceChild(newone, elm);
	
}


$(document).ready(function() {
	
	$current_id = 0;
	
    $.ajax({
          type: "GET",
          contentType: "application/json; charset=utf-8",
          url: "/api/current_user",
          success: function (response) {
                $('input[name=name]').val(response.name);
                $('input[name=username]').val(response.username);
                $('input[name=email]').val(response.email);
				$current_id = response.id;
          },
           dataType: "json"
});




$('form[name=form_update_n]').submit(function(event) {
    var obj = {
                'name' 	: $('input[name=name]').val(),
                'username' 	: $('input[name=username]').val(),
                'email' 	: $('input[name=email]').val()
            };
			
	console.log(obj);
    $.ajax({
          type: "PUT",
          contentType: "application/json; charset=utf-8",
          url: "/api/user/" + $current_id,
          data: JSON.stringify(obj),
		  
		  
          success: function (response) {
				warn_error('User update success')
                $('input[name=name]').val(response.name);
                $('input[name=username]').val(response.username);
                $('input[name=email]').val(response.email);
          },
          dataType: "json",
			error: function() {
					warn_error('Invalid information')
			}
});
event.preventDefault();
});

$('form[name=form_update_p]').submit(function(event) {
    var obj = {
                'password_a' 	: $('input[name=password_a]').val(),
				'password_n' 	: $('input[name=password_n]').val()
            };
			
	console.log(obj);
    $.ajax({
          type: "PUT",
          contentType: "application/json; charset=utf-8",
          url: "/api/userpw/" + $current_id,
          data: JSON.stringify(obj),
		  
		  
          success: function (response) {
				warn_error('Password update success')
                $('input[name=password_a]').val('');
				$('input[name=password_n]').val('');
          },
          dataType: "json",
	error: function() {
			warn_error('Wrong password')
	}
});
event.preventDefault();
});

});

