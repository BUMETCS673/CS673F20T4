//index page
function gomilk(id){
    window.open("products.html?category=milk&flag=true&id="+id,'_self');
}
//category
function category(p_category){
    cate = {'Category': p_category};

    $.ajax({
        url: '/products.html',
        type: "post",
        data: JSON.stringify(cate),
        dataType: 'json',
        contentType: "application/json; charset=utf-8"
    })
}

//cart empty alert
function emptycart(token){
    if($('#lblCartCount').text()=='0'){
        Swal.fire({
            icon: 'info',
            title: 'It seems your cart is empty',
            showConfirmButton: false,
            timer: 1500,
        });
    }else{
        window.location.replace('/cart');
    };
}

//login page
function closeeye(event){
    var _this = $(event.target);
    var openeye = _this;
    var closeeye = _this.next();
    var password = _this.closest('div').prev();

    password.attr('type','text')
    openeye.css('display','none');
    closeeye.css('display','block');
}

function openeye(event){
    var _this = $(event.target);
    var openeye = _this.prev();
    var closeeye = _this;
    var password = _this.closest('div').prev();

    password.attr('type','password')
    openeye.css('display','block');
    closeeye.css('display','none');
}

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

if(myInput){
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
}}


// product page
//loading more
		$(".card").slice(0, 8).show();
		$("#loadMore").on('click', function () {
   			$(".card:hidden").slice(0, 8).show();
    		if ($(".card:hidden").length == 0) {
       	 		$("#loadMore").fadeOut();
    		}
		});

//check if its from index page
var url = window.location.href;
var index = url.indexOf("flag");
if(index !=-1) {
    var start = url.indexOf("id");
    var id = "#"+url.substring(start + "id".length+1);
    $(id).click();
}

function updateCart(num, count) {
    var cart = $('#cart');
    var num_cart = document.getElementById("lblCartCount");
    //cart shake
    setTimeout(function () {
        cart.effect('shake', {times: 2}, 200);
    }, 800);
    //update num in carts
    num = num + count;
    num_cart.style.display = 'inline';
    $('#lblCartCount').text(num);
}

//register page
function register(event) {
    var first_name = document.getElementById("firstname").value;
    var last_name = document.getElementById("lastname").value;
    var email_address = document.getElementById("email").value;
    var password_2 = document.getElementById("password2").value;
    var password_3 = document.getElementById("password3").value;
    if(email_address.substring(email_address.length - 3, email_address.length) =='edu'){
        Swal.fire({
            icon: 'info',
            title: 'Sorry, we currently do not accept the education email',
            showConfirmButton: false,
            timer: 1800,
        });
    }else{
    if (first_name && last_name && email_address && password_2 && password_3) {
        register_info = {
            first_name: first_name,
            last_name: last_name,
            email_address: email_address,
            password_2: password_2,
            password_3: password_3
        };
        $.ajax({
            url: '/register-result',
            type: "post",
            data: JSON.stringify(register_info),
            dataType: 'json',
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                if (data != 'OK') {
                    Swal.fire({
                        icon: 'error',
                        title: 'Oops...',
                        text: data,
                        showConfirmButton: true,
                    });
                } else {
                    window.location.replace('/index.html')
                }
            }
        })
    } else {
        Swal.fire({
            icon: 'error',
            title: 'Oops...',
            text: 'Your information cannot be empty!',
            showConfirmButton: true,
        });
    }
    }
}
//forget password
function forget_password(event){
    var email = $('#email').val();
    if(email.length==0){
        Swal.fire({
            icon: 'info',
            text: 'Please fill in your email address.',
            showConfirmButton: false,
            timer: 1000,
            width: 200
        });
    }else{
        email_json = {email_address:email}

        $.ajax({
            url: '/forget-password',
            type: "post",
            data: JSON.stringify(email_json),
            dataType: 'json',
            contentType: "application/json; charset=utf-8"
        }).done(function (data) {
            Swal.fire({
            icon: 'success',
            text: 'The password reset link is sending to '+email,
            showConfirmButton: false,
            timer: 1500,
            });
        })
    }
}

//reset
function reset(event){
    var password1 = $('#for_password1').val();
    var password2 = $('#for_password2').val();
    var passwords = {
            password1: password1,
            password2: password2
        };

    var lowerCaseLetters = /[a-z]/g;
    var upperCaseLetters = /[A-Z]/g;
    var numbers = /[0-9]/g;

    var text = '';
    if (password1 == '' || password2 == '') {
        var text = 'Password cannot be empty!'
    } else if (password1.length > 20 || password1.length < 8) {
        var text = 'Password length should between 8-20!'
    } else if (password1.match(lowerCaseLetters) == null) {
        var text = 'Password should have at least one lower case letter!'
    } else if (password1.match(upperCaseLetters) == null) {
        var text = 'Password should have at least one upper case letter!'
    } else if (password1.match(numbers) == null) {
        var text = 'Password should have at least one number!'
    } else if (password1 != password2) {
        var text = 'New password and confirm password should be same!'
    };
    if(text!=''){
        Swal.fire({
          icon: 'error',
          title: 'Oops...',
          text: text,
        })
    }else{
        $.ajax({
            url: '/forget-reset',
            type: "post",
            data: JSON.stringify(passwords),
            dataType: 'json',
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                if (data == 'True') {
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
                } else {
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


// fly to cart 
function addCart(pid) {
    var s_left = event.clientX;
    var s_top = event.clientY;
    var e_left = $("#cart").offset().left;
    var e_top = $("#cart").offset().top;
    var _this = $(event.target);
    var img = '../static/css/images/'+pid+'.png'

    var flyer = $("<img src='" + img + "' width='50' style='border-radius:50%'/>");

    var num = parseInt($('#lblCartCount').text());


    flyer.css({'z-index': 10000});
    flyer.fly({
        start: {
            left: s_left,
            top: s_top
        },
        end: {
            left: e_left,
            top: e_top
        },
        onEnd: function () {
            flyer.fadeOut("slow", function () {
                $(this).remove();
            });
        },
    });
    updateCart(num, 1);

    product_to_cart = {id:pid,quantity:1};

    $.ajax({
        url: '/product2cart',
        type: "post",
        data: JSON.stringify(product_to_cart),
        dataType: 'json',
        contentType: "application/json; charset=utf-8"
    })

}


// pop window
function popwindow(event) {
    var _this = $(event.target);
    var img = _this.attr("src");
    var pid = _this.attr("id");
    var layer = document.getElementById("pop-layer");
    var box = document.getElementById("pop-box");;
    //display pop box
    if (img) {
        var price = _this.next();
        var name = price.next();
        var vol = name.next();
        var brand = vol.next();
        var description = brand.next();
        var specialty = description.next();
        var description_txt = description.html().replace(/\n/g, '<br/>');

        layer.style.display = 'block';
        box.style.display = 'block';
        $('.product-detail-pic').attr('src', img);
        $('.product-detail-pic').attr('id', pid);
        $('#product-name').text(name.text());
        $('#product-vol').text(vol.text());
        $('#product-price').text(price.text());
        $('#product-brand').text("brand: "+brand.text());
        $('#product-specialty').text(specialty.text());
        $('#product-des').html(description_txt);

        $(document).ready(function () {
            $('.product-detail-pic')
                .wrap('<span style="display:inline-block"></span>')
                .css('display', 'block')
                .parent()
                .zoom();
        });
        $('.product-detail-pic').zoom(); // add zoom
        $('.product-detail-pic').trigger('zoom.destroy'); // remove zoom
    } else {
        layer.style.display = 'none';
        box.style.display = 'none';
    }
}

//pop box add to cart
function PopaddCart(event) {
    var cart = $('#cart');
    var count = document.getElementById("select-num").value;
    var num = parseInt($('#lblCartCount').text())
    var pid = $('.product-detail-pic').attr('id')

    updateCart(num, parseInt(count));
    Swal.fire({
        icon: 'success',
        title: 'Added to cart',
        showConfirmButton: false,
        timer: 1000,
        width: 200
    });

    product_to_cart = {id:pid,quantity:count}
    $.ajax({
        url: '/product2cart',
        type: "post",
        data: JSON.stringify(product_to_cart),
        dataType: 'json',
        contentType: "application/json; charset=utf-8"
    })

}

// open pic
function imgShow(event) {
    var src = $("#product-detail-pic").attr("src");
    var newTab = window.open("");
    setTimeout(function () {
        newTab.document.write("<img src='" + src + "'>");
    });

    return false
}


//cart page
function updatenum(event) {
    var _this = $(event.target);
    var input = _this.closest('div').find('input');
    var pid =  _this.closest('div').prev().prev().find('img').attr('id');
    var value = parseInt(input.val());
    var _class = _this.attr("id");
    var price_loc = _this.closest('div').next();
    //unit price
    var price = parseFloat(price_loc.attr("value"));
    var subtotal = parseFloat($('#cart-subtotal').text().slice(1));
    var current_cart = parseInt($('#lblCartCount').text());

    //update quantity for each prod
    if (_class == "plus-btn") {
        var change_type='+';
        value++
        subtotal += price
        $('#lblCartCount').text(current_cart+1);
    } else {
        $('#lblCartCount').text(current_cart-1);
         var change_type='-';
        if (value > 1) {
            value--
            subtotal -= price
        } else {
            _this.closest('.item').remove();
            subtotal -= price;
            }
        };

    $('#cart-subtotal').text('$'+subtotal.toFixed(2))
    if(subtotal >= 35){
        document.getElementById("freeshipping").style.display = "none"
        $('#cart-shipping').text('$'+0);
    }else{
        document.getElementById("freeshipping").style.display = "block"
        var need_price = 35-subtotal;
        $('#freeshipping').text('Add'+' $'+need_price.toFixed(2)+' more to have a FREE delivery!');
        $('#cart-shipping').text('$'+7);
    }
    var total = (parseFloat($('#cart-shipping').text().slice(1))+parseFloat($('#cart-subtotal').text().slice(1))).toFixed(2);

    $('#cart-total').text('$'+total);

    input.val(value);
    var total_price = (price * value).toFixed(2)
    price_loc.text("$"+total_price);

    item_change = {change_type:change_type,pid:pid};
    $.ajax({
        url: '/cartchange',
        type: "post",
        data: JSON.stringify(item_change),
        dataType: 'json',
        contentType: "application/json; charset=utf-8"
    })


}

//remove from cart
function removefromcart(event) {
    var _this = $(event.target);
    var pid = _this.closest('.item').first('div').find('img').attr('id');
    var current_cart = parseInt($('#lblCartCount').text());
    var subtotal = parseFloat($('#cart-subtotal').text().slice(1));
    var cur_q = _this.closest('div').prev().prev().find('input').attr('value');
    var total_p = parseFloat(_this.closest('div').prev().text().slice(1));

    $('#cart-subtotal').text('$'+(subtotal-total_p).toFixed(2));
    if(subtotal-total_p >=35){
        document.getElementById("freeshipping").style.display = "none";

    }else{
       document.getElementById("freeshipping").style.display = "block";
       var need_price = 35-subtotal+total_p;
       $('#freeshipping').text('Add'+' $'+need_price.toFixed(2)+' more to have a FREE delivery!');
    };

    $('#cart-total').text('$'+(subtotal-total_p+parseInt($('#cart-shipping').text().slice(1))).toFixed(2));

    $('#lblCartCount').text(current_cart-cur_q);


    _this.closest('.item').remove();
    item_remove = {pid:pid};

    $.ajax({
        url: '/cartremove',
        type: "post",
        data: JSON.stringify(item_remove),
        dataType: 'json',
        contentType: "application/json; charset=utf-8"
    })

}

//profile
//add new address
$('select[name=address]').change(function () {
    if ($(this).val() == '') {
        Swal.fire({
            title: 'Add a new address',
            html:
                '<input id="address1" class="swal2-input" placeholder="Address line 1">' +
                '<input id="address2"  class="swal2-input" placeholder="Address line 2">' +
                '<input id="zip" class="swal2-input" placeholder="Zip code" maxlength="5" style="width:50%">' +
                '<label id="city" class="swal2-text" style="width:50%; text-align:center;"></label>',
            confirmButtonText: 'Submit',
            confirmButtonColor: '#519D60',
            showCancelButton: true,
            cancelButtonColor: '#bdbfc4',
            preConfirm: function () {
                var street = String($('#address1').val()) + ', ' + String($('#address2').val())
                var zip = $('#zip').val();
                var city_state = String($("#city").val()).split(",");
                var city = city_state[0];
                var state = city_state[1];
                var address = {
                    street: street,
                    zip: zip,
                    city: city,
                    state: state
                };
                $.ajax({
                    url: '/profile/',
                    type: "post",
                    data: JSON.stringify(address),
                    dataType: 'json',
                    contentType: "application/json; charset=utf-8",
                    success: function (data) {
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
        $('#zip').blur(function () {

            var zip = $(this).val();
            var isValidZip = /^\d{5}(?:-\d{4})?$/.test(zip);
            var clientKey = "cvMdRnxLYaNeHM7cgDm7hwGgLST4ocYc0Yu4ABHMZ1BT8tDa0fp0fgskmzgwcqUb";
            var url = "https://www.zipcodeapi.com/rest/" + clientKey + "/info.json/" + zip + "/radians";
            var container = $("#city");

            if (isValidZip) {
                Swal.resetValidationMessage();
                $.ajax({
                    "url": url,
                    "dataType": "json"
                }).done(function (data) {
                    container.text(data.city + ' , ' + data.state);
                })
            } else (
                Swal.showValidationMessage('Please enter a valid Zip Code')
            )
        });
    }
});

//change name
function changename(event) {
    var _this = $(event.target);
    var prev_text = _this.closest('div').prev().find('span');
    var save_button = $("<button class='change' onclick='savename(event)'>Save</button>");
    _this.replaceWith(save_button);
    var input = $("<input class='form-control' id='inputname' value='" + prev_text.text() + "' onkeydown='if(event.keyCode==13) return false;' />");

    prev_text.replaceWith(input);

};

//save change
function savename(event) {
    var _this = $(event.target);
    var input = _this.closest('div').prev().find('input');
    var type = _this.closest('div').prev().prev().text();
    var new_text = $("<span>" + input.val() + "</span>");
    input.replaceWith(new_text);

    var change_button = $("<button class='change' id='change-name' onclick='changename(event)'>Change</button>");
    _this.replaceWith(change_button);

    var name = {type_name: [type, input.val()]}

    $.ajax({
        url: '/profile/',
        type: "post",
        data: JSON.stringify(name),
        dataType: 'json',
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if (data == 'True') {
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
                    title: 'Your ' + type + ' has been changed successfully'
                })
            }
        }
    })
}


//change password
function changepassword(event) {
    Swal.fire({
        title: 'Change Password',
        html:
            '<input id="currentpassword" type="password" class="swal2-input" placeholder="Current Password">' +
            '<input id="newpassword1" type="password" class="swal2-input" placeholder="New Password">' +
            '<input id="newpassword2" type="password" class="swal2-input" placeholder="Confirm New Password">',
        confirmButtonText: 'Submit',
        confirmButtonColor: '#519D60',
        showCancelButton: true,
        cancelButtonColor: '#bdbfc4',

        preConfirm: function () {
            var currentpassword = $('#currentpassword').val();
            var password1 = $('#newpassword1').val();
            var password2 = $('#newpassword2').val();
            var passwords = {
                currentpassword: currentpassword,
                password1: password1,
                password2: password2
            };

            var lowerCaseLetters = /[a-z]/g;
            var upperCaseLetters = /[A-Z]/g;
            var numbers = /[0-9]/g;
            if (currentpassword == '' || password1 == '' || password2 == '') {
                Swal.showValidationMessage('Password cannot be empty!')
            } else if (password1.length > 20 || password1.length < 8) {
                Swal.showValidationMessage('Password length should between 8-20!')
            } else if (password1.match(lowerCaseLetters) == null) {
                Swal.showValidationMessage('Password should have at least one lower case letter!')
            } else if (password1.match(upperCaseLetters) == null) {
                Swal.showValidationMessage('Password should have at least one upper case letter!')
            } else if (password1.match(numbers) == null) {
                Swal.showValidationMessage('Password should have at least one number!')
            } else if (password1 != password2) {
                Swal.showValidationMessage('New password and confirm password should be same!')
            } else {
                $.ajax({
                    url: '/profile/',
                    type: "post",
                    data: JSON.stringify(passwords),
                    dataType: 'json',
                    contentType: "application/json; charset=utf-8",
                    success: function (data) {
                        if (data == 'True') {
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
                        } else {
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
function updateaddress(event) {
    address = {address: $("#select-address option:selected").text(),key: $("#select-address option:selected").val()};

    $.ajax({
        url: '/updateaddress',
        type: "post",
        data: JSON.stringify(address),
        dataType: 'json',
        contentType: "application/json; charset=utf-8",
        success: function (data) {
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
// change payment
function updatepayments(event) {
    payment = {key: $("#select-payment option:selected").val(),payment: $("#select-payment option:selected").text()}
    $.ajax({
        url: '/updatepayment',
        type: "post",
        data: JSON.stringify(payment),
        dataType: 'json',
        contentType: "application/json; charset=utf-8",
        success: function (data) {
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
                title: 'You have successfully changed the default payment !'
            })
        }
    })
}


function force_login(event) {
    Swal.fire({
        icon: 'warning',
        title: 'Please login',
        confirmButtonText: 'OK',
        confirmButtonColor: '#519D60',
        showCancelButton: true,
        cancelButtonColor: '#bdbfc4',
        preConfirm: function () {
            window.location.replace("login.html")
        }
    })
}

//login
function login(event){
      var email = $('#email').val();
      var password = $('#password1').val();
      var data = {email:email,password:password};

      $.ajax({
        url: '/login-result',
        type: "post",
        data: JSON.stringify(data),
        dataType: 'json',
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if (data=="none") {
                Swal.fire({
                    icon: 'warning',
                    title: 'It seems you have not registered',
                    width: 500,
                    showCancelButton: true,
                    cancelButtonColor: '#c9c9c9',
                    confirmButtonText: 'Sign Up Now!',
                    confirmButtonColor: '#519D60',
                }).then((result)=>{
                    if(result.isConfirmed){
                        window.location.href = 'register.html'
                    }
                })
            }else if(data=="wrong"){
                Swal.fire({
                    icon: 'warning',
                    title: 'Your password is incorrect!',
                    width: 500
                });
            }else {
                document.cookie = data['token'];
                window.location.href = '/index.html'
            }
        }

})
}

//logout
function logout(event){
    $.ajax({
        url: '/log-out',
        type: "post",
        dataType: 'json',
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            window.location.replace('index.html');
        }
    });
}
//account_setting
function account_setting(event){
    var account = {data: 'hey,bro'};
    $.ajax({
        url: '/profile-account',
        type: "post",
        dataType: 'json',
        data: JSON.stringify(account),
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if(data=="True"){
                window.location.replace('/profile-account');
            }else{
                alert('oops');
            }
        }
    });
}

//account_setting
function order_history(event){
    var account = {data: 'hey,bro'};
    $.ajax({
        url: '/profile-account',
        type: "post",
        dataType: 'json',
        data: JSON.stringify(account),
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if(data=="True"){
                window.location.replace('/profile-order');
            }else{
                alert('oops');
            }
        }
    });
}

function vieworder(orderid){
    order = {order_id:orderid}
    $.ajax({
        url: '/order-detail',
        type: "post",
        dataType: 'json',
        data: JSON.stringify(order),
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            window.location.replace('/order-detail')
        }
    });

}