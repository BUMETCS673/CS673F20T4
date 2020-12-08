var CartTotal = 0;
var TaxPrice = 0;
var DeliveryFees = 5;
var MainTotal = 0;

const DeliveryFeesReference = {
	standard:{
		cost: 5,
		displayName: "Standard"
	},
	priority:{
		cost: 7.99,
		displayName: "Priority"
	},
	nextDay:{
		cost: 12.99,
		displayName: "Next Day"
	}
}

const CreditCardInfos = [
	{
		cardType: "Mastercard",
		endingWith: 6969
	},

	{
		cardType: "Visa",
		endingWith: 4205
	},

	{
		cardType: "American Express",
		endingWith: 4242
	}
]

const AddressInfos = [
	{
		street: "800 Boylston St",
		city: "Boston",
		state: "MA",
		postalCode: "02199"
	},
	{
		street: "53 Huntington Ave",
		city: "Boston",
		state: "MA",
		postalCode: "02200"
	}

]

const TaxPrecentage = 0.05; //5% Precent Tax

function onDropDownBtnClick(element){
	let parentContainer = element.parentElement.parentElement;
	let dropDownContent = parentContainer.getElementsByClassName("dropDownContent")[0];

	element.classList.toggle("selected");
	dropDownContent.classList.toggle("opened");
}

function generateDeliveryFeePlanOptions(defaultOption=""){
	var planTemplate = document.getElementById("optionsTemplate");
	var feeOptionsElement = document.getElementById("deliveryFeeOptions");

	for (let optionName in DeliveryFeesReference){
		let option = DeliveryFeesReference[optionName];

		let planElement = planTemplate.content.cloneNode(true);

		planElement.querySelector("input").id = optionName;
		planElement.querySelector("input").value = optionName;

		planElement.querySelector("label").htmlFor = optionName;
		planElement.querySelector("label").innerHTML = `${option.displayName} Delivery $${option.cost.toFixed(2)}`;

		feeOptionsElement.appendChild(planElement);
	}

	//Sets starting/default Option
	setDeliveryFeePlan(defaultOption);

} generateDeliveryFeePlanOptions("standard"); //Runs at startup


function generateCardInfos(defaultCard=0){
	var creditCardInfosElement = document.getElementById("creditCardInfos");
	for(let id in CreditCardInfos){
		let card = CreditCardInfos[id];
		let optionElement = document.createElement("OPTION");

		optionElement.value = `card-${id}`;
		optionElement.innerHTML = `xxxx xxxx xxxx ${card.endingWith} - ${card.cardType}`

		creditCardInfosElement.appendChild(optionElement);
	}
	setCard(`card-${defaultCard}`);
} generateCardInfos(0)

function generateAddressInfos(defaultAddress=0){
	var addressInfosElement = document.getElementById("addressInfos");
	for(let id in AddressInfos){
		let address = AddressInfos[id];
		let optionElement = document.createElement("OPTION");

		optionElement.value = `address-${id}`;
		console.log(address);
		optionElement.innerHTML = `${address.street}, ${address.city}, ${address.state} ${address.postalCode}`;

		addressInfosElement.appendChild(optionElement);
	}
	setAddress(`address-${defaultAddress}`);
} generateAddressInfos(0)

function setDeliveryFeePlan(plan){
	if(!DeliveryFeesReference.hasOwnProperty(plan))return new Error("No Delivery Plan Exists");
	DeliveryFees = DeliveryFeesReference[plan].cost;

	document.getElementById(plan).checked = true;
	updateReceiptInfo();
}

function setCard(cardId){
	let id = cardId.split("-")[1];
	let card = CreditCardInfos[id];

	document.getElementById("creditCardInfo").innerHTML = `${card.cardType} ending with ${card.endingWith}`
	document.getElementById("creditCardInfos").value = cardId;
}

function setAddress(addressId){
	let id = addressId.split("-")[1];
	let address = AddressInfos[id];

	document.getElementById("address-primary").innerHTML = `${address.street}`
	document.getElementById("address-secondary").innerHTML = `${address.city}, ${address.state} ${address.postalCode}`
}

class ItemList{
	constructor(listData = {}, listName = ""){
		this.list = listData;
		this.listName = listName;
		this.length = Object.keys(this.list).length;
		this.totalCost = 0;
	}

	addItem(item){
		if(this.isItemExist(item.name))return new Error("Item Already Exists!");
		this.list[item.name] = item;
		this.totalCost += item.cost * item.qty;
		this.length++;
		this.onUpdate(this);
	}

	removeItem(itemName){
		if(!this.isItemExist(itemName))return new Error("Item is not found in List!");
		this.totalCost-=this.list[itemName].cost;
		delete this.list[itemName];
		this.length--;
		this.onUpdate(this);
	}

	isItemExist(itemName){
		return this.list.hasOwnProperty(itemName);
	}

	setOnUpdateMehtod(method){
		this.onUpdate = method;
	}
}

class Item{
	constructor(name, displayName, cost = 0, qty = 1, imgUrl){
		this.name = name;
		this.displayName = displayName;
		this.cost = cost;
		this.qty = qty;
		this.img = imgUrl;
	}
}

function updateItemListInfo(listObject){

	document.getElementById("numberOfItems").innerHTML = `${listObject.length} Item${listObject.length!=1?"s":""}`;
	
	CartTotal = listObject.totalCost;

	updateReceiptInfo();

	var itemTemplate = document.getElementById("itemTemplate");
	var itemListElement = document.getElementById("shoppingItemList");

	itemListElement.innerHTML = "";

	for (let itemName in listObject.list) {
		if (listObject.list.hasOwnProperty(itemName)) {
			let item = listObject.list[itemName];
			let itemElement = itemTemplate.content.cloneNode(true);

			itemElement.querySelector(".itemImg").src = item.img;
			itemElement.querySelector(".itemName").innerHTML = item.displayName;
			itemElement.querySelector(".itemCost").innerHTML = `${item.cost.toFixed(2)} Qty.${item.qty}`;

			itemListElement.appendChild(itemElement);

		}
	}
}

function updateReceiptInfo(){
	TaxPrice =  (DeliveryFees + CartTotal) * TaxPrecentage;
	MainTotal = TaxPrice + CartTotal + DeliveryFees;

	document.getElementById("price-txt").innerHTML = `$${CartTotal.toFixed(2)}`;
	document.getElementById("deliveryFees-txt").innerHTML = `$${DeliveryFees.toFixed(2)}`;
	document.getElementById("tax-txt").innerHTML = `$${TaxPrice.toFixed(2)}`;
	document.getElementById("total-txt").innerHTML = `$${MainTotal.toFixed(2)}`;
}

var checkoutItemList = new ItemList({}, "Checkout List");
checkoutItemList.setOnUpdateMehtod(updateItemListInfo);

checkoutItemList.addItem(new Item('milk1', 'Organic Milk', 3.60, 2, 'css/images/milk1.jpg'));
checkoutItemList.addItem(new Item('milk2', 'Whole Milk', 5.47, 1, 'css/images/milk2.jpeg'));
checkoutItemList.addItem(new Item('milk3', 'Oat Milk', 10.63, 1, 'css/images/milk3.jpg'));