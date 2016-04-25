<?php

session_start();

if ($_SESSION["Login"] != "YES") {
	header ("Location: index.php");
	header('Cache-Control: no-cache, must-revalidate');
	header('Expires: Mon, 26 Jul 1997 05:00:00 GMT');	
}
function SendTCP($in, $address, $port){
	
	/* Create a TCP/IP socket. */
	$socket = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
	$result = socket_connect($socket, $address, $port);
	$out = '';
	socket_write($socket, $in, strlen($in));
	while ($out = socket_read($socket, 2048)) {
	}
	socket_close($socket);
}
if(isset($_POST['XMLUPDATE']))
{
	SendTCP("XMLUpdate", '*IPADDRESS', 8889);
}
?>

<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<META HTTP-EQUIV="CACHE-CONTROL" CONTENT="NO-CACHE">
<META HTTP-EQUIV="PRAGMA" CONTENT="NO-CACHE">
<script src = "jquery-1.7.1.min.js"></script>
<script>

var TimeArray = new Array();

for (i = 0;i<98;i++){

   TimeArray[i] = false;
}

function changeText(idElement) {

    var element = document.getElementById('element' + idElement);
        if (TimeArray[idElement] == false){
           element.style.background = 'red';
           TimeArray[idElement] = true;
           //alert (TimeArray[idElement]);
        }
        else {
            element.style.background = '#1985FF';
            TimeArray[idElement] = false;
			//alert (TimeArray[idElement]);
        }
	
}

function sleep(milliseconds) {
	var start = new Date().getTime();
	for (var i = 0; i<1e7; i++) {
		if ((new Date().getTime() - start) > milliseconds) {
			break;
		}
	}
}
function loadGridStatus()
{	
	var i;

	for (i = 1; i < 98; i++)
	{
		var elementObj = document.getElementById('element' + i);
		if (TimeArray[i] == false){
			elementObj.style.background = '#1985FF';
			//alert ("TESTING FALSE");
		}
		else if (TimeArray[i] == true){
			elementObj.style.background = 'red';
			//alert ("TESTING TRUE");
		}
	}
}

function loadJSON() 
{
	$.ajaxSetup({
		'async' : false,
		'cache' : false,
		'timeout' : 5000
		});
	$.getJSON('json.txt')
		.done (function(data)
		{
			for (var i=0, len=data.length; i < len; i++ ) {
				console.log(data[i]);
				TimeArray[i] = data[i];
			}
		
	});
}
function saveJSON()
{
	var myJsonString = JSON.stringify(TimeArray, true);
	$.post("json.php", myJsonString);
	$.post("heating2.php", "XMLUPDATE");
	setTimeout(ReloadPage, 1000);
}
function ClearAll()
{
	for (i = 0;i<98;i++){
		TimeArray[i] = false;
	}
	saveJSON();
	setTimeout(ReloadPage, 1000);
}
function ReloadPage()
{	
	location.reload(true);
}
loadJSON();

</script>
</head>
<style>
	html,body,td,th {
		width: 100%
		height: 100%
		margin: 0;
		padding: 0;
		color: #CCCCCC;
		background-color: #000000;
		font-family: Arial, Helvetica, sans-serif;
	}
	body {
		background-color: #000000;
	}
	.btn {
		-webkit-border-radius: 9;
		-moz-border-radius: 0;
		-webkit-appearance: none;
		border-radius: 9px;
		text-shadow: 5px 1px 3px #666666;
		font-family: Arial;
		color: #ffffff;
		font-size: 20px;
		background: #808080;
		padding: 10px 18px 12px 15px;
		text-decoration: none;
		}
	.btn:hover {
		background: #593cfc;
		background-image: -webkit-linear-gradient(top, #593cfc, #3498db);
		background-image: -moz-linear-gradient(top, #593cfc, #3498db);
		background-image: -ms-linear-gradient(top, #593cfc, #3498db);
		background-image: -o-webkit-linear-gradient(top, #593cfc, #3498db);
		background-image: linear-gradient(to bottom, #593cfc, #3498db);
		text-decoration: none;
		}
		
</style>
<body onload='loadJSON()'>

<table border="1" style="background-color:#1985FF;border:1px dotted black;width:8%;border-collapse:collapse;">

<tr>
<td><a id="element1" onClick="javascript:changeText(1)">00:00</a></td>
<td><a id="element9" onClick="javascript:changeText(9)">02:00</a></td>
<td><a id="element17" onClick="javascript:changeText(17)">04:00</a></td>
<td><a id="element25" onClick="javascript:changeText(25)">06:00</a></td>
<td><a id="element33" onClick="javascript:changeText(33)">08:00</a></td>
<td><a id="element41" onClick="javascript:changeText(41)">10:00</a></td>
<td><a id="element49" onClick="javascript:changeText(49)">12:00</a></td>
<td><a id="element57" onClick="javascript:changeText(57)">14:00</a></td>
<td><a id="element65" onClick="javascript:changeText(65)">16:00</a></td>
<td><a id="element73" onClick="javascript:changeText(73)">18:00</a></td>
<td><a id="element81" onClick="javascript:changeText(81)">20:00</a></td>
<td><a id="element89" onClick="javascript:changeText(89)">22:00</a></td>
</tr>
<tr>
<td><a id="element2" onClick="javascript:changeText(2)">00:15</a></td>
<td><a id="element10" onClick="javascript:changeText(10)">02:15</a></td>
<td><a id="element18" onClick="javascript:changeText(18)">04:15</a></td>
<td><a id="element26" onClick="javascript:changeText(26)">06:15</a></td>
<td><a id="element34" onClick="javascript:changeText(34)">08:15</a></td>
<td><a id="element42" onClick="javascript:changeText(42)">10:15</a></td>
<td><a id="element50" onClick="javascript:changeText(50)">12:15</a></td>
<td><a id="element58" onClick="javascript:changeText(58)">14:15</a></td>
<td><a id="element66" onClick="javascript:changeText(66)">16:15</a></td>
<td><a id="element74" onClick="javascript:changeText(74)">18:15</a></td>
<td><a id="element82" onClick="javascript:changeText(82)">20:15</a></td>
<td><a id="element90" onClick="javascript:changeText(90)">22:15</a></td>
</tr>
<tr>
<td><a id="element3" onClick="javascript:changeText(3)">00:30</a></td>
<td><a id="element11" onClick="javascript:changeText(11)">02:30</a></td>
<td><a id="element19" onClick="javascript:changeText(19)">04:30</a></td>
<td><a id="element27" onClick="javascript:changeText(27)">06:30</a></td>
<td><a id="element35" onClick="javascript:changeText(35)">08:30</a></td>
<td><a id="element43" onClick="javascript:changeText(43)">10:30</a></td>
<td><a id="element51" onClick="javascript:changeText(51)">12:30</a></td>
<td><a id="element59" onClick="javascript:changeText(59)">14:30</a></td>
<td><a id="element67" onClick="javascript:changeText(67)">16:30</a></td>
<td><a id="element75" onClick="javascript:changeText(75)">18:30</a></td>
<td><a id="element83" onClick="javascript:changeText(83)">20:30</a></td>
<td><a id="element91" onClick="javascript:changeText(91)">22:30</a></td>
</tr>
<tr>
<td><a id="element4" onClick="javascript:changeText(4)">00:45</a></td>
<td><a id="element12" onClick="javascript:changeText(12)">02:45</a></td>
<td><a id="element20" onClick="javascript:changeText(20)">04:45</a></td>
<td><a id="element28" onClick="javascript:changeText(28)">06:45</a></td>
<td><a id="element36" onClick="javascript:changeText(36)">08:45</a></td>
<td><a id="element44" onClick="javascript:changeText(44)">10:45</a></td>
<td><a id="element52" onClick="javascript:changeText(52)">12:45</a></td>
<td><a id="element60" onClick="javascript:changeText(60)">14:45</a></td>
<td><a id="element68" onClick="javascript:changeText(68)">16:45</a></td>
<td><a id="element76" onClick="javascript:changeText(76)">18:45</a></td>
<td><a id="element84" onClick="javascript:changeText(84)">20:45</a></td>
<td><a id="element92" onClick="javascript:changeText(92)">22:45</a></td>
</tr>
<tr>
<td><a id="element5" onClick="javascript:changeText(5)">01:00</a></td>
<td><a id="element13" onClick="javascript:changeText(13)">03:00</a></td>
<td><a id="element21" onClick="javascript:changeText(21)">05:00</a></td>
<td><a id="element29" onClick="javascript:changeText(29)">07:00</a></td>
<td><a id="element37" onClick="javascript:changeText(37)">09:00</a></td>
<td><a id="element45" onClick="javascript:changeText(45)">11:00</a></td>
<td><a id="element53" onClick="javascript:changeText(53)">13:00</a></td>
<td><a id="element61" onClick="javascript:changeText(61)">15:00</a></td>
<td><a id="element69" onClick="javascript:changeText(69)">17:00</a></td>
<td><a id="element77" onClick="javascript:changeText(77)">19:00</a></td>
<td><a id="element85" onClick="javascript:changeText(85)">21:00</a></td>
<td><a id="element93" onClick="javascript:changeText(93)">23:00</a></td>
</tr>
<tr>
<td><a id="element6" onClick="javascript:changeText(6)">01:15</a></td>
<td><a id="element14" onClick="javascript:changeText(14)">03:15</a></td>
<td><a id="element22" onClick="javascript:changeText(22)">05:15</a></td>
<td><a id="element30" onClick="javascript:changeText(30)">07:15</a></td>
<td><a id="element38" onClick="javascript:changeText(38)">09:15</a></td>
<td><a id="element46" onClick="javascript:changeText(46)">11:15</a></td>
<td><a id="element54" onClick="javascript:changeText(54)">13:15</a></td>
<td><a id="element62" onClick="javascript:changeText(62)">15:15</a></td>
<td><a id="element70" onClick="javascript:changeText(70)">17:15</a></td>
<td><a id="element78" onClick="javascript:changeText(78)">19:15</a></td>
<td><a id="element86" onClick="javascript:changeText(86)">21:15</a></td>
<td><a id="element94" onClick="javascript:changeText(94)">23:15</a></td>
</tr>
<tr>
<td><a id="element7" onClick="javascript:changeText(7)">01:30</a></td>
<td><a id="element15" onClick="javascript:changeText(15)">03:30</a></td>
<td><a id="element23" onClick="javascript:changeText(23)">05:30</a></td>
<td><a id="element31" onClick="javascript:changeText(31)">07:30</a></td>
<td><a id="element39" onClick="javascript:changeText(39)">09:30</a></td>
<td><a id="element47" onClick="javascript:changeText(47)">11:30</a></td>
<td><a id="element55" onClick="javascript:changeText(55)">13:30</a></td>
<td><a id="element63" onClick="javascript:changeText(63)">15:30</a></td>
<td><a id="element71" onClick="javascript:changeText(71)">17:30</a></td>
<td><a id="element79" onClick="javascript:changeText(79)">19:30</a></td>
<td><a id="element87" onClick="javascript:changeText(87)">21:30</a></td>
<td><a id="element95" onClick="javascript:changeText(95)">23:30</a></td>
</tr>
<tr>
<td><a id="element8" onClick="javascript:changeText(8)">01:45</a></td>
<td><a id="element16" onClick="javascript:changeText(16)">03:45</a></td>
<td><a id="element24" onClick="javascript:changeText(24)">05:45</a></td>
<td><a id="element32" onClick="javascript:changeText(32)">07:45</a></td>
<td><a id="element40" onClick="javascript:changeText(40)">09:45</a></td>
<td><a id="element48" onClick="javascript:changeText(48)">11:45</a></td>
<td><a id="element56" onClick="javascript:changeText(56)">13:45</a></td>
<td><a id="element64" onClick="javascript:changeText(64)">15:45</a></td>
<td><a id="element72" onClick="javascript:changeText(72)">17:45</a></td>
<td><a id="element80" onClick="javascript:changeText(80)">19:45</a></td>
<td><a id="element88" onClick="javascript:changeText(88)">21:45</a></td>
<td><a id="element96" onClick="javascript:changeText(96)">23:45</a></td>

</tr>


</table>
<ul class="button-group">
	<button type="button" class="btn" onclick="saveJSON(); loadJSON();loadGridStatus();"> Save </button>
	<button type="button" class="btn" onclick="loadJSON();loadGridStatus();"> Cancel </button>
	<button type="button" class="btn" onclick="ClearAll(); loadGridStatus();"> Clear All </button>
	<button type="button" class="btn" onclick="window.location.href='heating.php'"> Finished </button>
</ul>
	
<script> 

loadGridStatus();
</script>

</body>
<head>
<META HTTP-EQUIV="PRAGMA" CONTENT="NO-CACHE">
</head>
</html>
