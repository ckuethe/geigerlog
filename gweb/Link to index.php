<?php
// Web Page: View GMC WiFi Output
// Example:  http://10.0.0.20/gmc/?AID=1&GID=2&CPM=99&ACPM=11.34&uSV=0.123

function print_r2($val){
    echo '<pre>';
    print_r($val);
    echo  '</pre>';
}
?>
<!DOCTYPE html>
<html lang="en">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
<meta charset="utf-8" />
<link rel="stylesheet" href="/css">
<link rel="icon" type="image/png" href="/favicon.ico" sizes="16x16">
<style>
    div     {max-width:380px;}
    table   {border:solid;}
    td,th   {padding:8px 0px 8px 3px; font-size:50px; width:200px; height:150px; border:solid; text-align:center;}
    td, th  {font-weight:900;}
    p       {margin-bottom:0px; font-weight:normal;}
</style>

<title>GeigerLog GMC Viewer</title>
<table>
    <tr>
        <td>CPM</td>
        <td>ACPM</td>
        <td>µSv/h</td>
    </tr>
    <tr>
        <?php
            $gets = explode("&", parse_url($_SERVER['REQUEST_URI'], PHP_URL_QUERY));
            // echo print_r2($gets);
            $CPM  = -1;
            $ACPM = -1;
            $uSV  = -1;
            foreach($gets as $p){
                $paramData = explode("=",$p);
                if     ($paramData[0] == "CPM")  {$CPM  = $paramData[1];}
                else if($paramData[0] == "ACPM") {$ACPM = $paramData[1];}
                else if($paramData[0] == "uSV")  {$uSV  = $paramData[1];}
            }
        ?>
        <td style="background-color:cyan;"      ><?php echo $CPM  ?></td>
        <td style="background-color:lightgreen;"><?php echo $ACPM ?></td>
        <td style="background-color:yellow;"    ><?php echo $uSV  ?></td>
    </tr>
</table>

