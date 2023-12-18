<?php 
  
// Complex array 
$string = 'a:2:{s:22:"stock_modifier_handler";a:3:{s:6:"finded";i:0;s:16:"sold_in_shipping";i:0;s:5:"tries";a:2:{s:7:"product";i:0;s:7:"general";i:0;}}s:24:"pricing_modifier_handler";a:2:{s:6:"finded";d:0;s:5:"tries";a:5:{s:7:"product";b:0;s:3:"tag";b:0;s:8:"category";b:0;s:5:"brand";b:0;s:7:"general";b:0;}}}';
// Unserializing the data in $string 
$newvar = unserialize($string); 
  
// Printing the unserialized data 
print_r($newvar); 