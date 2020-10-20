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