set -ex

echo "Stage 1B: Validating metadata"
echo "Starting tests for received metadata"

TARGET_SCORE=$(head -2 target_score.txt | tail -1)
if [[ ${TARGET_SCORE} == 4 ]]; then
  echo "Running score four checks"
  python -m unittest config/raw_metadata_score_four_test.py
elif [[ ${TARGET_SCORE} == 6 ]]; then
  echo "Running score six checks"
  python -m unittest config/raw_metadata_score_six_test.py
elif [[ ${TARGET_SCORE} == 8 ]]; then
  echo "Running score eight checks"
  python -m unittest config/raw_metadata_test.py
else
  echo "Running score ten checks"
  python -m unittest config/raw_metadata_test.py
fi

echo "Raw data is checked. Done"
