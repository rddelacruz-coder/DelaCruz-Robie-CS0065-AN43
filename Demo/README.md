# Student Performance Prediction

This project is a classroom demonstration of a supervised classification workflow that predicts whether a student is **At Risk** or **Not At Risk** using four academic indicators. The dataset is synthetic and must not be used for real student decisions.

## Project files

- `student_performance.csv` — dataset used by KNIME and Python
- `Student_Performance_Prediction.knwf` — exported KNIME workflow
- `evidence.pdf` — screenshots of the completed workflow and application

## Dataset and prediction target

Input features:

- `attendance`
- `quiz_score`
- `assignment_score`
- `exam_score`

Target column: `risk_status`

Excluded column: `student_id`, because it is only a row identifier and should not influence predictions.

## Algorithms compared

1. Logistic Regression
2. Decision Tree
3. Random Forest

The Python comparison uses stratified five-fold cross-validation with random state `42`. Accuracy, precision, recall, and F1-score are reported for the **At Risk** class. Logistic Regression is saved as the final classroom model because it is simple and interpretable; the small synthetic dataset is not sufficient for deployment.