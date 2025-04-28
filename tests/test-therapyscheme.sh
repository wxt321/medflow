# v6-生成多方案

curl -X 'POST' \
  'http://ip:port/inference?request_type=v6&scheme=pick_therapy' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d @data/therapyscheme-picktherapy.json

  echo -e "\n==================================\n"

curl -X 'POST' \
  'http://ip:port/inference?request_type=v6&scheme=generate_therapy&sub_scheme=default_therapy' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d @data/therapyscheme-generatetherapy.json

  echo -e "\n==================================\n"

curl -X 'POST' \
  'http://ip:port/inference?request_type=v6&scheme=generate_medicine&sub_scheme=default_therapy' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d @data/therapyscheme-generatemedicine.json

  echo -e "\n==================================\n"