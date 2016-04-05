

	<html>

	<head>
	<title>RasPi Heating Login</title>

	</head>
	<body>
	
	<?php

	// Check if username and password are correct
	if ($_POST["username"] == "*WebUSER" && $_POST["password"] == "*WebPASS") {
	 
	// If correct, we set the session to YES
	  session_start();
	  $_SESSION["StartTime"] = date("r");
	  $_SESSION["Login"] = "YES";
	  echo "<h1>Login Correct</h1>";
	  header('Refresh: 2; URL=heating.php');
	  //echo "<p><a href = 'heating.php'> Link</a><p/>";
	}
	else {
	 
	// If not correct, we set the session to NO
	  session_start();
	  $_SESSION["StartTime"] = date("r");
	  $_SESSION["Login"] = "NO";
	  echo "<h1>Login Incorrect</h1>";
	  header('Refresh: 2; URL=index.php');

	}
	$strTest = $_SESSION["Login"];
	echo "<p>Test String = " . $strTest . "<p>";
	echo "<p>Session Start time = " . $_SESSION["StartTime"] . "<p>";
	?>

	</body>
	</html>
