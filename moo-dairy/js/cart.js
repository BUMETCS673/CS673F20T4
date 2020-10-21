var num = 0;

function addCart(event) {
	var s_left =event.clientX;
	var s_top =event.clientY;
	var e_left =$("#cart").offset().left;
	var e_top =$("#cart").offset().top;
	var _this =$(event.target);
	var img = _this.prev().siblings("img").attr("src");
	var flyer = $("<img src='"+img+"' width='50' style='border-radius:50%'/>");
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
		}
	});
	
	num++;  
	$('#cart').text(num);
}