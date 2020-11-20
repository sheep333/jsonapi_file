for i in $(find ./outputs/json_outputs -maxdepth 1 -type f -name "*.json");
do
  name=$(basename "$i" ".json")
  mkdir -p "./output/jsonl/$name"
  jq -c ".data[]" $i |tee -a "./output/jsonl/$name/$name.jsonl";
done
