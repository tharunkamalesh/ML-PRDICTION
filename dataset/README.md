# Symptom–Disease Benchmark Dataset Documentation

## Overview
This dataset represents a standardized clinical mapping of 131 clinical symptoms across 41 medical conditions. It is patterned after standard educational and benchmark datasets for disease classification, aligning symptom presentations with clinical manifestation patterns.

## Dataset Structure
- **Features (`X`)**: 131 binary indicator variables (0 = absent, 1 = present) covering general, respiratory, cardiovascular, dermatological, gastrointestinal, musculoskeletal, and neurological symptoms.
- **Target (`y`)**: `prognosis` (categorical string representing one of 41 clinical conditions).
- **Files**:
  - `training_data.csv`: 3,936 stratified samples (80%) for training and cross-validation.
  - `testing_data.csv`: 984 stratified held-out samples (20%) reserved strictly for evaluation without data leakage.
  - `full_dataset.csv`: 4,920 combined records.

## Data Quality Assurance
- **Missing Values**: 0 missing values across all columns.
- **Stratification**: Balanced distribution across all 41 diagnostic categories.
- **Leakage Prevention**: Feature scaling/encoders are fit strictly on training splits.
- **Noise Modeling**: Probabilistic variations and co-occurrence noise are included to reflect realistic patient reporting discrepancies.

## Ethical & Clinical Notice
This dataset and all derived machine learning models are designed for **academic and educational screening assistance only**. They do not constitute diagnostic medical devices and must not be used to replace direct evaluation by qualified medical personnel.
