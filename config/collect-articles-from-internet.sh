set -ex

echo "Stage: Downloading articles"

python config/config_param_changer.py

echo "Changed config params"

python scrapper.py

echo "Collected dataset"

echo "Checking volume of files"

TARGET_SCORE=$(head -2 target_score.txt | tail -1)
if [[ ${TARGET_SCORE} == 4 ]]; then
  echo "Running score four checks"
  python -m unittest config/check_raw_dataset_volume_score_four_test.py
else
  python -m unittest config/check_raw_dataset_volume_test.py
fi

echo "Volume is correct"
