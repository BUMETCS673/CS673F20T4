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