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
	var _class =  _this.attr("class");
	var price_loc = _this.closest('div').next();
	var price = parseFloat(price_loc.attr("value"));	

	if (_class=="plus-btn"){
		value ++
	}else{
		if (value>0){
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
