<?php


session_start();

if ($_SESSION["Login"] != "YES") {
	header ("Location: index.php");
	header('Cache-Control: no-cache,no-store, must-revalidate');
	header('Expires: Mon, 26 Jul 1997 05:00:00 GMT');
	//header('Content-type: application/json');
	
}
	
echo "<h2>Heating @ Home</h2>\n";

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

?> 

<!DOCTYPE html>
<html>

<head>
</head>
<header>
<META HTTP-EQUIV="Refresh" CONTENT="5" "javascript:window.location = window.location.pathname; function1();">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta charset='utf-8'>
<meta HTTP-EQUIV='X-UA-Compatible' content='IE=Edge'>
</header>
<script>

function startInterval()
{
	setInterval("function1();", 2);
}

function function1()
{
    xmlhttp=new XMLHttpRequest();
    xmlhttp.open("GET","ButtonStatus.xml",false);
    xmlhttp.setRequestHeader("Pragma","no-cache");
    xmlhttp.setRequestHeader("Cache-Control","no-store, no-cache, must-revalidate");
    xmlhttp.send();
    xmlDoc=xmlhttp.responseXML; 
    var x=xmlDoc.getElementsByTagName("field");
    var numElements=x.length;
    console.log("Number of Elements in XML = "+numElements);
    var buttonStatusString = "";
    for (i=0; i<numElements; i++){
	buttonStatusString += x[i].childNodes[0].nodeValue;
        buttonStatusString += " | ";
    }
    console.log("XML = "+buttonStatusString);
 	
    if (x[0].childNodes[0].nodeValue == "True")
    {
        document.getElementById("Box1").style.backgroundColor = 'red';
    }
    else
    {
        document.getElementById("Box1").style.backgroundColor = 'grey';
    }
	if (x[7].childNodes[0].nodeValue == "True")
	{	
		document.getElementById("Box2").disabled=false;
		document.getElementById("Box3").disabled=false;
		if (x[1].childNodes[0].nodeValue == "True")
		{
			document.getElementById("Box2").style.backgroundColor = 'red';
		}
		else
		{
			document.getElementById("Box2").style.backgroundColor = 'grey';
		}
		if (x[2].childNodes[0].nodeValue == "True")
		{
			document.getElementById("Box3").style.backgroundColor = 'red';
		}
		else
		{
			document.getElementById("Box3").style.backgroundColor = 'grey';
		}
	}
	else 
	{
		document.getElementById("Box2").style.backgroundColor = 'dark-grey';
		document.getElementById("Box3").style.backgroundColor = 'dark-grey';
		document.getElementById("Box2").disabled=true;
		document.getElementById("Box3").disabled=true;
	}	
	if (x[3].childNodes[0].nodeValue == "True")
    {
        document.getElementById("Box4").style.backgroundColor = 'red';
    }
    else
    {
        document.getElementById("Box4").style.backgroundColor = 'grey';
    }
	document.getElementById("Box4").value = x[4].childNodes[0].nodeValue;
    if (x[5].childNodes[0].nodeValue == "True")
    {
        document.getElementById("Box5").style.backgroundColor = 'red';
    }
    else
    {
        document.getElementById("Box5").style.backgroundColor = 'grey';
    }
	if (x[6].childNodes[0].nodeValue == "True")
    {
        document.getElementById("Box6").style.backgroundColor = 'red';
    }
    else
    {
        document.getElementById("Box6").style.backgroundColor = 'grey';
    }
	if (x[8].childNodes[0].nodeValue == "True")
	{
		document.getElementById("statusCircle1").style.background = "red";
		document.getElementById("statusCircleText1").style.color = "yellow";
		document.getElementById("statusCircleText1").innerHTML = "ON";
	}
	else
	{
		document.getElementById("statusCircle1").style.background = "grey";
		document.getElementById("statusCircleText1").style.color = "black";
		document.getElementById("statusCircleText1").innerHTML = "OFF";
	}
	var OilLevel = parseInt(x[9].childNodes[0].nodeValue);
	document.getElementById("statusCircleText2").innerHTML = OilLevel;
	if (OilLevel < 50 )
	{
		document.getElementById("statusCircle2").style.background = "red";
	}
	if ((OilLevel >= 50 ) && (OilLevel < 100 ))
	{
		document.getElementById("statusCircle2").style.background = "yellow";
	}
	if (OilLevel >= 100 )
	{
		document.getElementById("statusCircle2").style.background = "green";
	}
	var outsideTemp = (x[10].childNodes[0].nodeValue);
	document.getElementById("statusCircleText3").innerHTML = outsideTemp;
	if (outsideTemp != "n/a"){
		outsideTemp = parseFloat(outsideTemp);
		if (outsideTemp > 30 )
		{
			document.getElementById("statusCircle3").style.background = "red";
		}
		if ((outsideTemp <= 30 ) && (outsideTemp > 20 ))
		{
			document.getElementById("statusCircle3").style.background = "yellow";
		}
		if ((outsideTemp <= 20 ) && (outsideTemp > 15 ))
		{
			document.getElementById("statusCircle3").style.background = "green";
		}
		if ((outsideTemp <= 15 ) && (outsideTemp > 10 ))
		{
		document.getElementById("statusCircle3").style.background = "aquamarine";
		}
		if ((outsideTemp <= 10 ) && (outsideTemp > 4 ))
		{
			document.getElementById("statusCircle3").style.background = "aqua";
		}
		if (outsideTemp <= 4 )
		{
			document.getElementById("statusCircle3").style.background = "blue";
		}
	}
	var BattLevel = (x[11].childNodes[0].nodeValue);
	document.getElementById("statusCircleText4").innerHTML = BattLevel;
	if (BattLevel != "n/a"){
		BattLevel = parseFloat(BattLevel);
	}
}
function function2(elm)
{
	window.location.href=elm;
}

</script>
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
		position: relative;
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
		background-image: -webkit-gradient(linear, left top, #593cfc, #3498db);
		background-image: -moz-linear-gradient(top, #593cfc, #3498db);
		background-image: -ms-linear-gradient(top, #593cfc, #3498db);
		background-image: -o-webkit-linear-gradient(top, #593cfc, #3498db);
		background-image: linear-gradient(to bottom, #593cfc, #3498db);
		text-decoration: none;
		}
	#statusCircle1 {
		position: relative;
		background-color: grey;
		margin: 20px auto;
		width: 100px;
		height: 100px;
		border-radius:200px
	}
	#statusCircleText1 {
		position: absolute;
		top: 50%;
		left: 50%;
		transform:translate(-50%, -50%);
		color: black;
		font-size: 40px;
	}
	#statusCircle2 {
		position: relative;
		background-color: grey;
		margin: 20px auto;
		width: 100px;
		height: 100px;
		border-radius:200px
	}
	#statusCircleText2 {
		position: absolute;
		top: 50%;
		left: 50%;
		transform:translate(-50%, -50%);
		color: black;
		font-size: 40px;
	}
#statusCircle3 {
		position: relative;
		background-color: grey;
		margin: 20px auto;
		width: 100px;
		height: 100px;
		border-radius:200px
	}
	#statusCircleText3 {
		position: absolute;
		top: 50%;
		left: 50%;
		transform:translate(-50%, -50%);
		color: black;
		font-size: 40px;
	}
#statusCircle4 {
		position: relative;
		background-color: grey;
		margin: 20px auto;
		width: 100px;
		height: 100px;
		border-radius:200px
	}
	#statusCircleText4 {
		position: absolute;
		top: 50%;
		left: 50%;
		transform:translate(-50%, -50%);
		color: black;
		font-size: 40px;
	}		
		
</style>
<body onload="function1();">
<form action="<?=$_SERVER['PHP_SELF'];?>" method="post">
	<ul class="button-group">
		
		<input type="submit" class="btn" id="Box1" name="submit1" value="    Off     " /> &nbsp
	
		<input type="submit" class="btn" id="Box2" name="submit2" value="  Upstairs " /> &nbsp
		
		<input type="submit" class="btn" id="Box3" name="submit3" value="Downstairs"/> &nbsp
		
	</ul>
	<ul class="button-group">
		
		<input type="submit" class="btn" id="Box4" name="submit4" value="   Timer    "/>	&nbsp
		
		<input type="submit" class="btn" id="Box5" name="submit5" value="   Timed   " /> &nbsp
		
		<input type="submit" class="btn" id="Box6" name="submit6" value="  Constant "/>	&nbsp
		
		
	</ul>
	
</form>

<div id = "statusCircle1">
	<div id = "statusCircleText1"> Relay </div> <br><br><br><br><br><br><center>Relay Status</center>
</div>
<table style = "width:100%">
<tr>
<td>
<div id = "statusCircle2">
	<div id = "statusCircleText2"> Oil </div> <br><br><br><br><br><br><center>Oil Level</center>
</div>
</td>
<td>
<div id = "statusCircle3">
	<div id = "statusCircleText3"> Temp </div> <br><br><br><br><br><br><center>Outside Temp</center>
</div>
</td>
<td>
<div id = "statusCircle4">
	<div id = "statusCircleText4"> Batt </div> <br><br><br><br><br><br><center>Battery Level</center>
</div>
</td>
</tr>
</table>



<?php 
if(isset($_POST['submit1']))
{
	SendTCP("Off", '*IPADDRESS', 8889);
	echo '<script type = "text/javascript">'
	, 'function1();'
	, 'document.getElementById("Box1").style.backgroundColor = "red";'
	, '</script>' 
	;
}
if(isset($_POST['submit2']))
{
	SendTCP("Upstairs", '*IPADDRESS', 8889);
	echo '<script type = "text/javascript">'
	, 'function1();'
	//, 'if (document.getElementById("Box2").style.backgroundColor = "red")'
	//, '{ document.getElementById("Box2").style.backgroundColor = "grey"; }'
	//, ' else { document.getElementById("Box2").style.backgroundColor = "red";}'
	, '</script>' 
	;
}
if(isset($_POST['submit3']))
{
	SendTCP("Downstairs", '*IPADDRESS', 8889);
	echo '<script type = "text/javascript">'
	, 'function1();'
	//, 'if (document.getElementById("Box3").style.backgroundColor = "red")'
	//, '{ document.getElementById("Box3").style.backgroundColor = "grey"; }'
	//, ' else { document.getElementById("Box3").style.backgroundColor = "red";}'
	, '</script>' 
	;
}
if(isset($_POST['submit4']))
{
	SendTCP("Timer", '*IPADDRESS', 8889);
	echo '<script type = "text/javascript">'
	, 'function1();'
	, 'document.getElementById("Box4").style.backgroundColor = "red";'
	
	, '</script>' 
	;
}
if(isset($_POST['submit5']))
{
	SendTCP("Timed", '*IPADDRESS', 8889);
	echo '<script type = "text/javascript">'
	, 'document.getElementById("Box5").style.backgroundColor = "red";'
	, 'function2("heating2.php");'
	, '</script>' 
	;
}
if(isset($_POST['submit6']))
{
	SendTCP("Constant", '*IPADDRESS', 8889);
	echo '<script type = "text/javascript">'
	, 'function1();'
	, 'document.getElementById("Box6").style.backgroundColor = "red";'
	, '</script>' 
	;
}
?>

</body>
</html>

