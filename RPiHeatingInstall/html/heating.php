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
		document.getElementById("statusCircle").style.background = "red";
		document.getElementById("statusCircleText").style.color = "yellow";
		document.getElementById("statusCircleText").innerHTML = "ON";
	}
	else
	{
		document.getElementById("statusCircle").style.background = "grey";
		document.getElementById("statusCircleText").style.color = "black";
		document.getElementById("statusCircleText").innerHTML = "OFF";
	}
	var OilLevel = parseInt(x[9].childNodes[0].nodeValue)
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
	#statusCircle {
		position: relative;
		background-color: grey;
		margin: 20px auto;
		width: 100px;
		height: 100px;
		border-radius:200px
	}
	#statusCircleText {
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

<div id = "statusCircle">
	<div id = "statusCircleText"> Relay </div>
</div>
<div id = "statusCircle2">
	<div id = "statusCircleText2"> Oil </div>
</div>



<?php 
if(isset($_POST['submit1']))
{
	SendTCP("Off", '192.168.1.240', 8889);
	echo '<script type = "text/javascript">'
	, 'function1();'
	, 'document.getElementById("Box1").style.backgroundColor = "red";'
	, '</script>' 
	;
}
if(isset($_POST['submit2']))
{
	SendTCP("Upstairs", '192.168.1.240', 8889);
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
	SendTCP("Downstairs", '192.168.1.240', 8889);
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
	SendTCP("Timer", '192.168.1.240', 8889);
	echo '<script type = "text/javascript">'
	, 'function1();'
	, 'document.getElementById("Box4").style.backgroundColor = "red";'
	
	, '</script>' 
	;
}
if(isset($_POST['submit5']))
{
	SendTCP("Timed", '192.168.1.240', 8889);
	echo '<script type = "text/javascript">'
	, 'document.getElementById("Box5").style.backgroundColor = "red";'
	, 'function2("heating2.php");'
	, '</script>' 
	;
}
if(isset($_POST['submit6']))
{
	SendTCP("Constant", '192.168.1.240', 8889);
	echo '<script type = "text/javascript">'
	, 'function1();'
	, 'document.getElementById("Box6").style.backgroundColor = "red";'
	, '</script>' 
	;
}
?>

</body>
</html>

