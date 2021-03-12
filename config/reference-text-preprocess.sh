set -ex

echo "Stage 2B: Reference text preprocessing"
echo "Starting tests for admin dataset"

TARGET_SCORE=$(head -5 target_score.txt | tail -1)
if [[ ${TARGET_SCORE} == 4 ]]; then
  echo "Running score four checks"
  python -m unittest config/reference_text_preprocess_score_four_test.py
elif [[ ${TARGET_SCORE} == 6 ]]; then
  echo "Running score six checks"
  python -m unittest config/reference_text_preprocess_test.py
elif [[ ${TARGET_SCORE} == 8 ]]; then
  echo "Running score eight checks"
  python -m unittest config/reference_text_preprocess_score_eight_test.py
  echo "TBD: later"
else
  echo "Running score ten checks"
  python -m unittest config/reference_text_preprocess_score_eight_test.py
  echo "TODO: check for PosFrequencyPipeline"
  echo "TBD: later"
fi

echo "Raw data is checked. Done"
