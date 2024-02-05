<?php 
  
// Complex array 
$myvar = [
    "total_payments_paid_amount" => 247.73,
]; 
  
// Convert to a string 
$string = serialize($myvar); 
  
// Printing the serialized data 
echo $string; 