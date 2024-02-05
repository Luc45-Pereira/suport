<?php 
  
// Complex array 
$string = 'a:4:{i:0;a:3:{s:11:"attributeId";s:15:"VISCOSITY_GRADE";s:8:"value_id";s:8:"17998053";s:10:"value_name";s:5:"0W-40";}i:1;a:3:{s:11:"attributeId";s:11:"UNIT_VOLUME";s:8:"value_id";s:8:"13183571";s:10:"value_name";s:3:"4 L";}i:2;a:3:{s:11:"attributeId";s:4:"LINE";s:8:"value_id";s:8:"22282191";s:10:"value_name";s:31:"10w40 Sintético Rubia Tir 8600";}i:3;a:3:{s:11:"attributeId";s:12:"VEHICLE_TYPE";s:8:"value_id";s:8:"15300913";s:10:"value_name";s:20:"Caminhões e ônibus";}}';
$newvar = unserialize($string); 
  
// Printing the unserialized data 
print_r($newvar); 
echo $newvar;
// $date = new DateTime('2024-01-23T17:50:49.000-04:00');
// print_r($date);
// echo $date->format('Y-m-d H:i:s');

// $date->setTimezone(new DateTimeZone('America/Sao_Paulo'));
// print_r($date);
// echo $date->format('Y-m-d H:i:s');

// $date->setTimezone(new DateTimeZone('America/Argentina/Buenos_Aires'));
// print_r($date);
// echo $date->format('Y-m-d H:i:s');

