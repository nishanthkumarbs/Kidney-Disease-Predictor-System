
$("#btnsignup").click(function(){
	debugger;
	alert('aaa')
	var uname=document.getElementById('name').value;
	var pswd=document.getElementById('pswd').value;
	var email=document.getElementById('email').value;
	var phone=document.getElementById('phone').value;
	var addr=document.getElementById('addr').value;
	var dob=document.getElementById('dob').value;
	
	  if (document.getElementById('uname').value =='' &&
	            document.getElementById('pswd').value =='' && document.getElementById('email').value =='' &&
                 document.getElementById('phone').value =='' && document.getElementById('addr').value =='')
	        {
	            alert('Please Fill All Fields');
	        }
       var flag = true;

	        var unamer = document.getElementById('uname').value;
	        var intRegexunamer = /^[A-Za-z 0-9]+$/;
	        if (!intRegexunamer.test(unamer)) {
	            alert('Please enter a valid name.');
				 $('#uname').css('border-color', 'Red');
	            flag = false;
	            return flag;
	        }
	        else {
				 $('#uname').css('border-color', 'white');
	            flag = true;
	        }

	        
			var namer = document.getElementById('pswd').value;
	        var intRegexnamer = /^[A-Za-z0-9 ]+$/;
	        if (!intRegexnamer.test(namer)) {
	            alert('Please enter password.');
				 $('#pswd').css('border-color', 'Red');
	            flag = false;
	            return flag;
	        }
	        else {
				 $('#pswd').css('border-color', 'white');
	            flag = true;
	        }
	        var email = document.getElementById('email').value;
	        var emailReg = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
	        if (!emailReg.test(email) || email == '') {
	            alert('Please enter a valid email id.');
				 $('#email').css('border-color', 'Red');
	            flag = false;
	            return flag;
	        }
	        else {
				$('#email').css('border-color', 'white');
	            flag = true;
	        }


	        var phone = document.getElementById('phone').value;
	        var intRegex = /^(7|8|9)[0-9]{9}$/;
	        if (!intRegex.test(phone)) {
	            alert('Please enter a valid phone number.');
				$('#phone').css('border-color', 'Red');
	            flag = false;
	            return flag;
	        }
	        else {
				$('#phone').css('border-color', 'white');
	            flag = true;
	        }
			
			var phone = document.getElementById('addr').value;
	        if (phone=='') {
	            alert('Please enter address.');
				$('#addr').css('border-color', 'Red');
	            flag = false;
	            return flag;
	        }
	        else {
				$('#addr').css('border-color', 'white');
	            flag = true;
	        }

	        //return flag;
	      //  return flag;
	    //}
	
	//var gender="";
	//if(document.getElementById('gen').checked==true)
	//	gender="Male";
	//if(document.getElementById('gen1').checked==true)
	//	gender="Female";
	
	/* window.location='regdata?uname='+uname+'&name='+name+'&pswd='+pswd+'&email='+email+'&phone='+phone+'&addr='+addr;*/
	
	$.ajax({
            type: 'GET',
            url: '/regdata',
			
        contentType: 'application/json;charset=UTF-8',
            data: {
            'uname': uname,
            'dob': dob,
            'email': email,
            'phone': phone,
            'pswd': pswd,
            'addr': addr
        },
            
        dataType:"json",
            success: function(data) {
				alert('Data saved Successfully');
				acheck();
              // window.location='register';
            },
        });
	
});



$("#btnlogsubmit").click(function(){
	debugger;
	var email=document.getElementById('email').value;
	var pswd=document.getElementById('pswd').value;
	 if (document.getElementById('email').value =='' && document.getElementById('pswd').value =='')
	        {
	            alert('Please Enter email and password');
	        }
	
	
	//var gender="";
	//if(document.getElementById('gen').checked==true)
	//	gender="Male";
	//if(document.getElementById('gen1').checked==true)
	//	gender="Female";
	
	/* window.location='regdata?uname='+uname+'&name='+name+'&pswd='+pswd+'&email='+email+'&phone='+phone+'&addr='+addr;*/
	
	$.ajax({
            type: 'GET',
            url: '/logdata',
			
        contentType: 'application/json;charset=UTF-8',
            data: {
            'email': email,
            'pswd': pswd
			

        },
            
        dataType:"json",
            success: function(data) {
				if(data=="Failure")
				{
					alert("Credentials not found");
					window.location='register';
				}
				if(data=="Success")
				{
					alert('Logged in Successfully');
				   window.location='dataloader';
				}
            },
			 error: function(data) {
               
            }
        });
	
});

function acheck()
{
	debugger;
}


$("#process_btnsubmit").click(function(){
	debugger;	
	window.location="/procdataset?data=sun";
});



$("#btnfetcluster").click(function(){
	debugger;	
	
	var reg=document.getElementById('regfor').value;
	window.location='/fetcluster?reg='+reg;
});


$("#btnpredict").click(function(){
	debugger;	
	
	var reg=document.getElementById('regfor').value;
	window.location='/predictrain?reg='+reg;
});


$("#dataload_btnsubmit").click(function(){
	debugger;
   var form_data = new FormData($('#upload-file')[0]);
        $.ajax({
            type: 'POST',
            url: '/uploadajax',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function(emotion) {
				alerter(emotion);
                console.log('Success!');
				//alert('Data stored successfully');
            },
        });
});

function alerter(data)
{
	debugger;
	console.log('sss');
}

$("#dataload_btnclear").click(function(){
   var form_data = new FormData($('#upload-file')[0]);
        $.ajax({
            type: 'POST',
            url: '/cleardataset',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function(data) {
                console.log('Success!');
				alert('Dataset has been cleared');
            },
        });
});
