# v6-生成多方案

ip=$1
port=$2
if [ -z "$ip" ] || [ -z "$port" ]; then
    echo "错误：请提供 IP 地址和端口号作为参数。"
    echo "用法：$0 <IP地址> <端口号>"
    exit 1
fi

curl -X 'POST' \
  "http://$ip:$port/inference?request_type=v6&scheme=pick_therapy" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d @data/therapyscheme-picktherapy.json

  echo -e "\n==================================\n"

curl -X 'POST' \
  "http://$ip:$port/inference?request_type=v6&scheme=generate_therapy&sub_scheme=default_therapy" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d @data/therapyscheme-generatetherapy.json

  echo -e "\n==================================\n"

curl -X 'POST' \
  "http://$ip:$port/inference?request_type=v6&scheme=generate_medicine&sub_scheme=default_therapy" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d @data/therapyscheme-generatemedicine.json

  echo -e "\n==================================\n"