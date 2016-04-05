//<html>
//<head>
//<title> TEST </title>
//</head>
//<body>


<?php
$file = fopen( "json.txt", "w");
$data = file_get_contents("php://input");
//$test = "Test2";
fwrite($file, $data);
fclose($file);

//$file = fopen("json.txt", "r");
//echo fgets($file);
//fclose($file);

?>

//</body>
//</html>

