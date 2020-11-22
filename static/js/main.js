function updateCart(num,count){
	var cart = $('#cart');
	var num_cart = document.getElementById("lblCartCount");
	//cart shake
	setTimeout(function () {
		cart.effect('shake', { times: 2 }, 200);
	}, 800);
	//update num in carts
	num=num+count;
	num_cart.style.display='inline';
	$('#lblCartCount').text(num);	
}


// fly to cart 
function addCart(event) {
	var s_left =event.clientX;
	var s_top =event.clientY;
	var e_left =$("#cart").offset().left;
	var e_top =$("#cart").offset().top;
	var _this =$(event.target);
	var img = _this.closest("div").find("img").attr("src");
	var flyer = $("<img src='"+img+"' width='50' style='border-radius:50%'/>");
	var num = parseInt($('#lblCartCount').text());
	
	flyer.css({'z-index':900});
	flyer.fly({
		start: {
			left:s_left,
			top:s_top
		},
		end: {
			left: e_left,
			top: e_top
		},
		onEnd:function(){
			flyer.fadeOut("slow",function(){
				$(this).remove();
			});
		},
	});
	
	updateCart(num,1);
}

// pop window
function popwindow(event) {
	var _this =$(event.target);
	var img = _this.attr("src");
	var price = _this.next().text();
	var name = _this.next().next().text();
	var vol = _this.next().next().next().text();
	var layer = document.getElementById("pop-layer");
	var box = document.getElementById("pop-box");

	//display pop box
	if(img){
		layer.style.display='block';
		box.style.display='block';
		$('.product-detail-pic').attr('src',img);
		$('#product-name').text(name);
		$('#product-vol').text(vol);
		$('#product-price').text(price);
		
		$(document).ready(function(){
		  $('.product-detail-pic')
		    .wrap('<span style="display:inline-block"></span>')
		    .css('display', 'block')
		    .parent()
		    .zoom();
		});
		$('.product-detail-pic').zoom(); // add zoom
		$('.product-detail-pic').trigger('zoom.destroy'); // remove zoom


	}else{
		layer.style.display='none';
		box.style.display='none';
	}
}

//pop box add to cart
function PopaddCart(event) {
	var cart = $('#cart');
	var count = document.getElementById("select-num").value;
	var num = parseInt($('#lblCartCount').text())
	updateCart(num,parseInt(count));
	Swal.fire({
	  icon: 'success',
	  title: 'Added to cart',
	  showConfirmButton: false,
	  timer: 1000,
	  width:200
	});
}

// open pic
function imgShow(event){
	var src=$("#product-detail-pic").attr("src");
	var newTab = window.open("");
	setTimeout(function(){
		newTab.document.write("<img src='"+src+"'>");
	});
	
	return false
}


//cart page
function updatenum(event){
	var _this =$(event.target);
	var input = _this.closest('div').find('input');
	var value = parseInt(input.val());
	var _class =  _this.attr("id");
	var price_loc = _this.closest('div').next();
	var price = parseFloat(price_loc.attr("value"));

	if (_class=="plus-btn"){
		value ++
	}else{
		if (value>1){
			value--
		}else{
			 _this.closest('.item').remove();
		}
	};
	input.val(value);
	
	price_loc.text("$"+price*value.toFixed(2));

}
//remove from cart
function removefromcart(event){
	var _this =$(event.target);
	_this.closest('.item').remove();
}

//profile
//add new address
$('select[name=address]').change(function() {
    if ($(this).val() == ''){
         Swal.fire({
              title: 'Add a new address',
              html:
                '<input id="address1" class="swal2-input" placeholder="Address line 1">' +
                '<input id="address2"  class="swal2-input" placeholder="Address line 2">'+
                '<input id="zip" class="swal2-input" placeholder="Zip code" maxlength="5" style="width:50%">'+
                '<label id="city" class="swal2-text" style="width:50%; text-align:center;"></label>',
              confirmButtonText: 'Submit',
              confirmButtonColor: '#519D60',
              showCancelButton: true,
              cancelButtonColor: '#bdbfc4',
              preConfirm: function() {
                var street = String($('#address1').val())+', '+String($('#address2').val())
                var zip = $('#zip').val();
                var city_state = String($("#city").val()).split(",");
                var city = city_state[0];
                var state = city_state[1];
                var address = {street: street,
                                 zip: zip,
                                 city: city,
                                 state:state};
                $.ajax({
                    url:'/profile/',
                    type:"post",
                    data: JSON.stringify(address),
                    dataType: 'json',
                    contentType: "application/json; charset=utf-8",
                    success:function (data) {
                             const Toast = Swal.mixin({
                              toast: true,
                              position: 'center',
                              showConfirmButton: false,
                              timer: 3000,
                              didOpen: (toast) => {
                                toast.addEventListener('mouseenter', Swal.stopTimer)
                                toast.addEventListener('mouseleave', Swal.resumeTimer)
                              }
                            })
                            Toast.fire({
                              icon: 'success',
                              title: 'You have successfully changed the default address !'
                            })
                    }
                 })
              }
              });
              $('#zip').blur(function(){

                var zip = $(this).val();
                var isValidZip = /^\d{5}(?:-\d{4})?$/.test(zip);
                var clientKey = "cvMdRnxLYaNeHM7cgDm7hwGgLST4ocYc0Yu4ABHMZ1BT8tDa0fp0fgskmzgwcqUb";
                var url = "https://www.zipcodeapi.com/rest/"+clientKey+"/info.json/" + zip + "/radians";
                var container = $("#city");

                if (isValidZip) {
                     Swal.resetValidationMessage();
                     $.ajax({
						"url": url,
						"dataType": "json"
					 }).done(function(data) {
						container.text(data.city+' , '+data.state);
					 })
                }else(
                    Swal.showValidationMessage('Please enter a valid Zip Code')
                )
              });
   }
});

//change name
function changename(event){
  var _this =$(event.target);
  var prev_text = _this.closest('div').prev().find('span');
  var save_button = $("<button class='change' onclick='savename(event)'>Save</button>");
  _this.replaceWith(save_button);
  var input = $("<input class='form-control' id='inputname' value='"+prev_text.text()+"' onkeydown='if(event.keyCode==13) return false;' />");

  prev_text.replaceWith( input );

};

//save change
function savename(event){
    var _this = $(event.target);
    var input = _this.closest('div').prev().find('input');
    var type = _this.closest('div').prev().prev().text();
    var new_text = $("<span>"+input.val()+"</span>");
    input.replaceWith(new_text);

    var change_button = $("<button class='change' id='change-name' onclick='changename(event)'>Change</button>");
    _this.replaceWith(change_button);

    var name = {type_name:[type,input.val()]}

    $.ajax({
        url:'/profile/',
        type:"post",
        data: JSON.stringify(name),
        dataType: 'json',
        contentType: "application/json; charset=utf-8",
        success:function (data) {
            if(data=='True'){
                const Toast = Swal.mixin({
                  toast: true,
                  position: 'center',
                  showConfirmButton: false,
                  timer: 3000,
                  didOpen: (toast) => {
                    toast.addEventListener('mouseenter', Swal.stopTimer)
                    toast.addEventListener('mouseleave', Swal.resumeTimer)
                  }
                })
                Toast.fire({
                  icon: 'success',
                  title: 'Your '+type+' has been changed successfully'
                })
            }
        }
            })
}


//change password
function changepassword(event){
    Swal.fire({
      title: 'Change Password',
      html:
        '<input id="currentpassword" type="password" class="swal2-input" placeholder="Current Password">' +
        '<input id="newpassword1" type="password" class="swal2-input" placeholder="New Password">'+
        '<input id="newpassword2" type="password" class="swal2-input" placeholder="Confirm New Password">',
      confirmButtonText: 'Submit',
      confirmButtonColor: '#519D60',
      showCancelButton: true,
      cancelButtonColor: '#bdbfc4',

      preConfirm: function() {
        var currentpassword = $('#currentpassword').val();
        var password1 = $('#newpassword1').val();
        var password2 = $('#newpassword2').val();
        var passwords = {currentpassword: currentpassword,
                         password1: password1,
                         password2: password2};

        var lowerCaseLetters = /[a-z]/g;
        var upperCaseLetters = /[A-Z]/g;
        var numbers = /[0-9]/g;
        if (currentpassword==''||password1==''||password2=='') {
            Swal.showValidationMessage('Password cannot be empty!')
        }else if(password1.length > 20 || password1.length < 8){
            Swal.showValidationMessage('Password length should between 8-20!')
        }else if(password1.match(lowerCaseLetters) == null){
            Swal.showValidationMessage('Password should have at least one lower case letter!')
        }else if(password1.match(upperCaseLetters)==null){
            Swal.showValidationMessage('Password should have at least one upper case letter!')
        }else if(password1.match(numbers)==null){
            Swal.showValidationMessage('Password should have at least one number!')
        }else if(password1!=password2){
            Swal.showValidationMessage('New password and confirm password should be same!')
        }else{
            $.ajax({
                url:'/profile/',
                type:"post",
                data: JSON.stringify(passwords),
                dataType: 'json',
                contentType: "application/json; charset=utf-8",
                success:function (data) {
                    if(data=='True'){
                        const Toast = Swal.mixin({
                          toast: true,
                          position: 'bottom-start',
                          showConfirmButton: false,
                          timer: 3000,
                          didOpen: (toast) => {
                            toast.addEventListener('mouseenter', Swal.stopTimer)
                            toast.addEventListener('mouseleave', Swal.resumeTimer)
                          }
                        })
                        Toast.fire({
                          icon: 'success',
                          title: 'You have successfully changed the password!'
                        })
                    }else{
                        Swal.fire({
                          icon: 'error',
                          title: 'Oops...',
                          text: 'Current password is not correct!'
                        })
                    }
                }
            })
        }
      }
    })
}

// change address
function updateaddress(event){
    address = {address: $("#select-address option:selected").text()}
    $.ajax({
        url:'/profile/',
        type:"post",
        data: JSON.stringify(address),
        dataType: 'json',
        contentType: "application/json; charset=utf-8",
        success:function (data) {
                 const Toast = Swal.mixin({
                  toast: true,
                  position: 'center',
                  showConfirmButton: false,
                  timer: 3000,
                  didOpen: (toast) => {
                    toast.addEventListener('mouseenter', Swal.stopTimer)
                    toast.addEventListener('mouseleave', Swal.resumeTimer)
                  }
                })
                Toast.fire({
                  icon: 'success',
                  title: 'You have successfully changed the default address !'
                })
        }
     })
}
