<?php
/*
Screaming Strike  simple update checker
Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
License: GPL V2.0 (See ../copying.txt for details)
*/

$latest="2.06";
if(isset($_REQUEST["updatecheck"])){
	if($_REQUEST["platform"]!="Windows" && $_REQUEST["platform"]!="Darwin"){
		returnError();
	}
	$filename=$_REQUEST["platform"].".log";
	if(!file_exists($filename)){
		$num=0;
		$fp=fopen($filename,"w");
		flock($fp,LOCK_EX);
	}else{
		$num=(int)file_get_contents($filename);
		$fp=fopen($filename,"w");
		flock($fp,LOCK_EX);
	}
$num++;
	fwrite($fp,"".$num."");
	flock($fp,LOCK_UN);
	fclose($fp);
	die($latest);
}
returnError();

function returnError(){
	die("error");
}

?>