<?php
$url = $_GET['url'];
$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'User-Agent: Instagram 255.0.0.19.109 (iPhone14,3; iOS 15_1; en_US)',
]);
$data = curl_exec($ch);
$info = curl_getinfo($ch);
curl_close($ch);

header("Content-Type: " . $info["content_type"]);
echo $data;
?>
