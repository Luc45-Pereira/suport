import phpserialize
import json

# String serializada PHP
serialized_php = 'a:2:{s:22:"stock_modifier_handler";a:3:{s:6:"finded";i:2;s:16:"sold_in_shipping";i:0;s:5:"tries";a:2:{s:7:"product";i:0;s:7:"general";i:2;}}s:24:"pricing_modifier_handler";a:2:{s:6:"finded";d:31;s:5:"tries";a:5:{s:7:"product";b:0;s:3:"tag";b:0;s:8:"category";b:0;s:5:"brand";b:0;s:7:"general";b:1;}}}'
php_data = phpserialize.loads(serialized_php)

# Extrair a parte que contém o JSON
json_string = php_data['last_response']['responseRaw']

# Carregar o JSON
json_data = json.loads(json_string)

# Exibir o JSON
print(json.dumps(json_data, indent=2))
