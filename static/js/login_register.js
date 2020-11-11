const eye1 = document.getElementById("eye1");
const pass1 = document.getElementById("password1");

if (eye1){
	//  SHOW / HIDE PASSWORD//
	eye1.addEventListener("click", function toggleEye1() {
	  var hideEye1 = document.getElementById("fa-eye-slash1");
	  var showEye1 = document.getElementById("fa-eye1");
		
	  if (pass1.type == "password") {
		pass1.setAttribute("type", "text");
		hideEye1.style.display = "block";
		showEye1.style.display = "none";
	  } else {
		pass1.setAttribute("type", "password");
		hideEye1.style.display = "none";
		showEye1.style.display = "block";
	  }
	});
}

const eye2 = document.getElementById("eye2");
const pass2 = document.getElementById("password2");

//  SHOW / HIDE PASSWORD//
if(eye2){
	eye2.addEventListener("click", function toggleEye2() {
	  var hideEye2 = document.getElementById("fa-eye-slash2");
	  var showEye2 = document.getElementById("fa-eye2");
		
	  if (pass2.type == "password") {
		pass2.setAttribute("type", "text");
		hideEye2.style.display = "block";
		showEye2.style.display = "none";
	  } else {
		pass2.setAttribute("type", "password");
		hideEye2.style.display = "none";
		showEye2.style.display = "block";
	  }
	});
}

const eye3 = document.getElementById("eye3");
const pass3 = document.getElementById("password3");

//  SHOW / HIDE PASSWORD//
if(eye3){
	eye3.addEventListener("click", function toggleEye3() {
	  var hideEye3 = document.getElementById("fa-eye-slash3");
	  var showEye3 = document.getElementById("fa-eye3");
		
	  if (pass3.type == "password") {
		pass3.setAttribute("type", "text");
		hideEye3.style.display = "block";
		showEye3.style.display = "none";
	  } else {
		pass3.setAttribute("type", "password");
		hideEye3.style.display = "none";
		showEye3.style.display = "block";
	  }
	});
}

//validation
//$.validator.setDefaults({
//            submitHandler: function () {
//               alert("success!");
//            }
//        });
        $().ready(function () {
            //login/register validation
            $(".login-form").validate({
                rules: {
					//password cannot be empty
                    password: {
                        required: true
                    },
					//email cannot be empty, must follow email format
                    email: {
                        required: true,
                        email: true
                    },
					firstname:{
						required:true
					},
					lastname:{
						required:true
					},
					//register password
					password2:{
						required: true,
						minlength: 8,
						maxlength:20
					},
					//register confirm password
					password3:{
						required: true,
						equalTo: "#password2"
					}
                },
				//tips style
                showErrors: function (errorMap, errorList) {
                    var msg = "";
                    $.each(errorList, function (i, v) {
                        layer.tips("<span style='color:black'>"+v.message+"</span>", v.element, { 
							time: 2000,
							tips:[1,'rgba(255, 255, 255, 0.8)']
							});
                        return false;
                    });  
                },
				//no focus remove tips
                onfocusout: false
            });
        });
		
		//password validation 
		var myInput = document.getElementById("password2");
		var letter = document.getElementById("letter");
		var capital = document.getElementById("capital");
		var number = document.getElementById("number");
		var length = document.getElementById("length");
		
		// When the user clicks on the password field, show the message box
		myInput.onfocus = function() {
		  document.getElementById("password-requirement").style.display = "block";
		}
		
		// When the user clicks outside of the password field, hide the message box
		myInput.onblur = function() {
		  document.getElementById("password-requirement").style.display = "none";
		}
		
		// When the user starts to type something inside the password field
		myInput.onkeyup = function() {
		  // Validate lowercase letters
		  var lowerCaseLetters = /[a-z]/g;
		  if(myInput.value.match(lowerCaseLetters)) {  
		    letter.classList.remove("invalid");
		    letter.classList.add("valid");
		  } else {
		    letter.classList.remove("valid");
		    letter.classList.add("invalid");
		  }
		  
		  // Validate capital letters
		  var upperCaseLetters = /[A-Z]/g;
		  if(myInput.value.match(upperCaseLetters)) {  
		    capital.classList.remove("invalid");
		    capital.classList.add("valid");
		  } else {
		    capital.classList.remove("valid");
		    capital.classList.add("invalid");
		  }
		
		  // Validate numbers
		  var numbers = /[0-9]/g;
		  if(myInput.value.match(numbers)) {  
		    number.classList.remove("invalid");
		    number.classList.add("valid");
		  } else {
		    number.classList.remove("valid");
		    number.classList.add("invalid");
		  }
		  
		  // Validate length
		  if(myInput.value.length >= 8 && myInput.value.length <= 20) {
		    length.classList.remove("invalid");
		    length.classList.add("valid");
		  } else {
		    length.classList.remove("valid");
		    length.classList.add("invalid");
		  }
		}

