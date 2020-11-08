

var num = 0;

// fly to cart 
function addCart(event) {
	var cart = $('#cart');
	var s_left =event.clientX;
	var s_top =event.clientY;
	var e_left =$("#cart").offset().left;
	var e_top =$("#cart").offset().top;
	var _this =$(event.target);
	var img = _this.prev().siblings("img").attr("src");
	var flyer = $("<img src='"+img+"' width='50' style='border-radius:50%'/>");
	var num_cart = document.getElementById("lblCartCount");
	flyer.css({
		'z-index':900
		});
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
	
	//cart shake
	setTimeout(function () {
		cart.effect('shake', { times: 2 }, 200);
	}, 800);
	
	//number in cart
	num++;
	num_cart.style.display='inline';  

	$('#lblCartCount').text(num);		
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
	}else{
		layer.style.display='none';
		box.style.display='none';
	}
}

//pop box add to cart
function PopaddCart(event) {
	var cart = $('#cart');
	var num_cart = document.getElementById("lblCartCount");
	var count = document.getElementById("select-num").value;

	//cart shake
	setTimeout(function () {
		cart.effect('shake', { times: 2 }, 200);
	}, 800);
	
	//number in cart
	num = num+parseInt(count);
	num_cart.style.display='inline';  

	$('#lblCartCount').text(num);	
	
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
