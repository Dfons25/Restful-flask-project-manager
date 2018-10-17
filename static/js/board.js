
$(document).ready(function() {
	

	$.date = function(dateObject) {
    var d = new Date(dateObject);
    var day = d.getDate();
    var month = d.getMonth() + 1;
    var year = d.getFullYear();
    if (day < 10) {
        day = "0" + day;
    }
    if (month < 10) {
        month = "0" + month;
    }
    var date = day + "/" + month + "/" + year;

    return date;
	};
	
	
	$.ajax({
		type: "GET",
		contentType: "application/json; charset=utf-8",
		url: "/api/current_user",
		success: function (response) {
		$('#user_name').text('Welcome ' + response.username);
		$('#user_id').val( response.id );

	},
	dataType: "json"
	});	   



	getUserProjects();

		
	$(function () {
		$("#datepicker").datepicker({ 
			format: 'dd/mm/yyyy',
			autoclose: true, 
			todayHighlight: true
		}).datepicker('update', new Date());
		});
});



function getUserProjects(){

	$.ajax({
		type: "GET",
		contentType: "application/json; charset=utf-8",
		url: "/api/projects" ,
		success: function (response) {
			
			var html = '<div id="#project_header" ><table class="table" width="300px"><tr><td>Insert a new Name and press Update on the corresponding project or create a new one</td><td></td></tr><tr><td><input name="project_name" placeholder="Name"/></td><td><button onclick="createProject()" class="btn btn-primary btn-block btn-large">Create</button></td></tr></table></div>'
			
			html += '<table class="table" id="projects_table"><tr><td>Name</td><td>Creation Date</td><td>Last Update</td><td></td></tr>';
			$.each(response, function (index, value) {
				html += '<tr><td>' + value['name'] + '</td><td>' + $.date(value['creation_date']) + '</td><td>' + $.date(value['last_updated']) + '</td><td><button onclick="getTask(' + value['id'] +  ')" class="btn btn-primary btn-block btn-large">Tasks</button></td><td><button onclick="updateProject(' + value['id'] +  ')" class="btn btn-primary btn-block btn-large">Update</button></td><td><button onclick="deleteProject(' + value['id'] +  ')" class="btn btn-primary btn-block btn-large">Delete</button></td></tr></tr>';
			});
		html += '</table>';
		$("#div_left").html(html);
		},
	dataType: "json",
		error: function() {
			var html = '<div id="#project_header" ><table class="table" width="300px"><tr><td>Insert a new Name and press Update on the corresponding project or create a new one</td><td></td></tr><tr><td><input name="project_name" placeholder="Name"/></td><td><button onclick="createProject()" class="btn btn-primary btn-block btn-large">Create</button></td></tr></table></div>'	
			html += '</table>';
			$("#div_left").html(html);
		}
	
});
}

function createProject() {
	
	var obj = {
                'name' 	: $('input[name=project_name]').val(),
                'user_id' 	: $('#user_id').val()
            };
			

    $.ajax({
          type: "POST",
          contentType: "application/json; charset=utf-8",
          url: "/api/projects",
          data: JSON.stringify(obj),
		  
		  
          success: function (response) {

				getUserProjects()				

          },
          dataType: "json",
	error: function() {
			warn_error('Project already exists')
	}
});
	
}


function updateProject(id){
	var obj = {
                'name' 	: $('input[name=project_name]').val(),
                'user_id' 	: $('#user_id').val()
            };
			
    $.ajax({
          type: "PUT",
          contentType: "application/json; charset=utf-8",
          url: "/api/projects/" + id,
          data: JSON.stringify(obj),
		  
		  
          success: function (response) {

				getUserProjects()				

          },
          dataType: "json",
	error: function() {
			warn_error('Project already exists')
	}
});	
}

function deleteProject(id){

			
    $.ajax({
          type: "DELETE",
          contentType: "application/json; charset=utf-8",
          url: "/api/projects/" + id,
		  
		  
          success: function (response) {

				getUserProjects();			
				getTask();
          },
          dataType: "json"
});	
}

function createTask(id) {
	
	var obj = {
                'title' 	: $('input[name=task_name]').val(),
                'user_id' 	: $('#user_id').val(),
				'due_date' : $('#datepicker').data('datepicker').getFormattedDate('yyyy-mm-dd'),
				'project_id' : id
            };
			

    $.ajax({
          type: "POST",
          contentType: "application/json; charset=utf-8",
          url: "/api/projects/" + id + "/tasks",
          data: JSON.stringify(obj),
		  
		  
          success: function (response) {
			getTask(id);
          },
          dataType: "json",
	error: function() {
			warn_error('Task already exists')
	}
});
	
}

function deleteTask(id){

			
    $.ajax({
          type: "DELETE",
          contentType: "application/json; charset=utf-8",
          url: "/api/projects/" + $('#project_id').val() + "/tasks/" + id,
		  
		  
          success: function (response) {
			getTask($('#project_id').val())
          },
          dataType: "json"
});	
}

function updateTask(id){
	
	if ($('#toggle' + id + '').prop('checked')){
		finish = 1;
	}else{
		finish = 0;
	}
	
	var obj = {
                'title' 	: $('input[name=task_name]').val(),
                'user_id' 	: $('#user_id').val(),
				'due_date' : $('#datepicker').data('datepicker').getFormattedDate('yyyy-mm-dd'),
				'completed' : finish
            };
			
    $.ajax({
          type: "PUT",
          contentType: "application/json; charset=utf-8",
          url: "/api/projects/" + $('#project_id').val() + "/tasks/" + id,
          data: JSON.stringify(obj),
		  
		  
          success: function (response) {
			getTask($('#project_id').val())
          },
          dataType: "json",
	error: function() {
			warn_error('Invalid data input')
	}
});	
}


function reorderTask(id, order, sum){
	
	var obj = {
                'order' : sum
            };
			
    $.ajax({
          type: "PUT",
          contentType: "application/json; charset=utf-8",
          url: "/api/projects/" + $('#project_id').val() + "/tasksReorder/" + id,
          data: JSON.stringify(obj),
		  
		  
          success: function (response) {
			getTask($('#project_id').val())
          },
          dataType: "json",
	error: function() {
			warn_error('Sync error')
	}
});	
}

function fillProjectName(id){
		$.ajax({

		type: "GET",
		contentType: "application/json; charset=utf-8",
		url: "/api/projects/" + id,
		success: function (response) {
			var html = '<tag id="proj_name">' + response.name + '</tag>' + '<br/>Due Date';
			$("#proj_name_tag").html(html);
		},
	dataType: "json"
});
}

function logoutUser(){
$.ajax({
          type: "GET",
          contentType: "application/json; charset=utf-8",
          url: "/api/user/logout/",
          dataType	: 'html',
          success: function (response) {
				window.location.href = '/app/user/logout'
		  }
});
}


function warn_error(message){
	
		elm = document.getElementById("toggle_opt_div");
		elm.innerHTML = '* ' + message + ' *';
		var newone = elm.cloneNode(true);
		elm.parentNode.replaceChild(newone, elm);
	
}


function getTask(id) {
	
	var div_right = document.getElementById('right_wrapper');
	
	$.ajax({

		type: "GET",
		contentType: "application/json; charset=utf-8",
		url:  "/api/projects/" + id + "/tasks",
		success: function (tasks) {
		
		
		$('#datepicker').css('visibility', 'visible');
		

		$('#project_id').val(id);
		
		var html = '<div id="#task_header" ><table class="table" width="300px"><tr><td>Insert a new Name or Due Date and press Update on the corresponding task or create a new one</td><td></td><td id="proj_name_tag"><br/>Due Date</td></tr><tr><td><input name="task_name" placeholder="Name"/></td><td><button onclick="createTask(' + id + ')" class="btn btn-primary btn-block btn-large">Create</button></td><td style="width: 205px;"></td></tr></table></div>';
			
		
		if (tasks.length > 0){
			html += '<table class="table" id="tasks_table"><tr><td>Order</td><td>Title</td><td>Creation Date</td><td>Due Date</td><td>Completed</td><td></td><td></td></tr>';
		}	
		//
		
		for (var i in tasks) {
			html += '<tr><td>'
			
			if(i != 0){
			html += '<button onclick=reorderTask(' + tasks[i].id +  ',' + tasks[i].order + ',(-1)) class="btn btn-primary btn-block btn-large btn-order">ʌ</button>'}
			
			html += tasks[i].order
			
			if(i != tasks.length - 1){
			html += '<button onclick=reorderTask(' + tasks[i].id +  ',' + tasks[i].order + ',1) class="btn btn-primary btn-block btn-large btn-order">v</button>'}
			
			html += '</td><td>' + tasks[i].title + '</td><td>' + $.date(tasks[i].creation_date) + '</td><td>' + $.date(tasks[i].due_date) + '</td><td><input id="toggle' + tasks[i].id + '" class="gen_toggle" type="checkbox"></td><td><button onclick=updateTask(' + tasks[i].id +  ') class="btn btn-primary btn-block btn-large">Update</button></td><td><button onclick=deleteTask(' + tasks[i].id +  ') class="btn btn-primary btn-block btn-large">Delete</button></td></tr>';
		}
		html += '</table>';
		div_right.innerHTML = html;
		
		$('.gen_toggle').bootstrapToggle({
		  on: 'True',
		  off: 'False'
		});
		
		for (var i in tasks) {
			if(tasks[i].completed == true){
				$('#toggle' + tasks[i].id + '').bootstrapToggle('on');
			}
			else{
				$('#toggle' + tasks[i].id + '').bootstrapToggle('off');
			}
			
		}
		
		fillProjectName(id);
		
		},
		dataType: "json",
		error: function() {

			warn_error('No tasks')

			$('#datepicker').css('visibility', 'visible');
			
			var html = '<div id="#task_header" ><table class="table" width="300px"><tr><td>Insert a new Name or Due Date and press Update on the corresponding task or create a new one</td><td></td><td id="proj_name_tag"><br/>Due Date</td></tr><tr><td><input name="task_name" placeholder="Name"/></td><td><button onclick="createTask(' + id + ')" class="btn btn-primary btn-block btn-large">Create</button></td><td style="width: 205px;"></td></tr></table></div>';
			html += '</table>';
			div_right.innerHTML = html;
		}		
});
}

