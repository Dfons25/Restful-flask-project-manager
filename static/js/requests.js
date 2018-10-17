function warn_error(message){
	
		elm = document.getElementById("toggle_opt_div");
		elm.innerHTML = '* ' + message + ' *';
		var newone = elm.cloneNode(true);
		elm.parentNode.replaceChild(newone, elm);
	
}

$(document).ready(function() {
    $('form[name=form_register]').submit(function(event) {
    var obj = {
                'name' 	: $('input[name=name_r]').val(),
                'username' 	: $('input[name=username_r]').val(),
                'email' 	: $('input[name=email_r]').val(),
                'password' 	: $('input[name=password_r]').val()
            };
			
	console.log(obj);
    $.ajax({
          type: "POST",
          contentType: "application/json; charset=utf-8",
          url: "/api/user/register/",
          data: JSON.stringify(obj),
		  
		  
          success: function (response) {
			    $('input[name=name_r]').val('');
                $('input[name=username_r]').val('');
                $('input[name=email_r]').val('');
                $('input[name=password_r]').val('');
                $('input[name=username_l]').val(response.username);
			 // }
          },
		  
          dataType: "json",
	error: function() {
			warn_error('Invalid data input')
	}
});
event.preventDefault();
});


    $('form[name=form_login]').submit(function(event) {
    var obj = {
                'username' 	: $('input[name=username_l]').val(),
                'password' 	: $('input[name=password_l]').val()
              };

	console.log(obj);
    $.ajax({
          type: "POST",
          contentType: "application/json; charset=utf-8",
          url: "/api/user/login/",
          data: JSON.stringify(obj),
          dataType	: 'html',
          success: function (response) {
			  
			if(response["redirect"]){
				window.location.href = response["redirect"]
			}
      	
		  },
           dataType: "json"	,
	error: function() {
			warn_error('Invalid data input')
	}
});
event.preventDefault();
});

});
