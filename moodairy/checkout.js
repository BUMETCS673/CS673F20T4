function onDropDownBtnClick(element){
	let parentContainer = element.parentElement.parentElement;
	let dropDownContent = parentContainer.getElementsByClassName("dropDownContent")[0];

	element.classList.toggle("selected");
	dropDownContent.classList.toggle("opened");
}