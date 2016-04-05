<html>
<head>
<title> RasPi Heating Login </title>

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
	#Form {
		position: relative;
		font-family: Helvetica;
		font-size: 40pt;
		
	}
	#User {
		position: relative;
		border: 1px solid blue;
		font-family: Helvetica;
		font-size: 40pt;
		padding: 0.1em;
		height: 100px;
		margin: 0.1em;
	}
	#Pass {
		position: relative;
		border: 1px solid red;
		font-family: Helvetica;
		font-size: 40pt;
		padding: 0.1em;
		height: 100px;
		margin: 0.1em;
	}
	#Enter {
		position: relative;
		border: 1px solid grey;
		font-family: Helvetica;
		font-size: 40pt;
		padding: 0.1em;
		height: 100px;
		margin: 0.1em;
	}
</style>
<body>
<form method = "post" id = "Form" action = "login.php">

<p> Username: <input type = "text" id = "User" name = "username" /></p>
<p> Password: <input type = "password" id = "Pass" name = "password" /></p>

<p><input type = "submit" value="Enter" id="Enter" /></p>

</form>
</body>
</html>

