---
name: ml-data-leakage-guard
description: Check ML features and preprocessing for prediction-time leakage.
version: 0.1.0
author: Vibe-Skills, Hermes Agent
license: Apache-2.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [upstream-adaptation, ml-data-leakage-guard]
    upstream_repository: "https://github.com/foryourhealth111-pixel/Vibe-Skills"
    upstream_commit: "ddcaa2affca93c1efe026d008b6b93709e5fb7e2"
---

# ML Data Leakage Guard Skill

Automatically detects and prevents data leakage in machine learning workflows by verifying that all preprocessing steps, feature engineering, and statistical computations would be available at prediction time.

## When to Use This Skill

Use this skill after work involving:
- Data preprocessing (normalization, standardization, scaling)
- Missing value imputation
- Feature engineering and feature selection
- Dimensionality reduction (PCA, SVD, t-SNE)
- Target encoding or label encoding
- Time series feature construction
- Data augmentation strategies
- Algorithm development and optimization
- Train-test split procedures
- Cross-validation setup

## Not For / Boundaries

- Pure theoretical ML discussions without implementation
- Model architecture design (without data preprocessing)
- Hyperparameter tuning (unless it involves data-dependent operations)

## Core Principle

**The Golden Rule**: At the exact moment of prediction in production, can I access this value from the database or compute it using only information available up to that point?

If the answer is "no" or "not completely", then data leakage exists.

## Quick Reference

### Critical Leakage Patterns

**Pattern 1: Preprocessing Before Split**
```python
# ❌ WRONG: Leakage - fit on entire dataset
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # Uses test set statistics
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y)

# ✅ CORRECT: Fit only on training data
X_train, X_test, y_train, y_test = train_test_split(X, y)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # Fit on train only
X_test_scaled = scaler.transform(X_test)  # Transform test using train statistics
```

**Pattern 2: Global Missing Value Imputation**
```python
# ❌ WRONG: Uses global statistics including test set
# (also: assign the result — Series.fillna(..., inplace=True) is a no-op
# under pandas copy-on-write)
df['age'] = df['age'].fillna(df['age'].mean())  # Global mean includes test data
X_train, X_test, y_train, y_test = train_test_split(df, y)

# ✅ CORRECT: Compute statistics on training set only
X_train, X_test, y_train, y_test = train_test_split(df, y)
train_mean = X_train['age'].mean()  # Only from training data
X_train['age'] = X_train['age'].fillna(train_mean)
X_test['age'] = X_test['age'].fillna(train_mean)  # Use train mean for test
```

**Pattern 3: PCA/Dimensionality Reduction on Full Dataset**
```python
# ❌ WRONG: PCA learns variance structure from test set
pca = PCA(n_components=10)
X_reduced = pca.fit_transform(X)  # Includes test set variance
X_train, X_test, y_train, y_test = train_test_split(X_reduced, y)

# ✅ CORRECT: Fit PCA only on training data
X_train, X_test, y_train, y_test = train_test_split(X, y)
pca = PCA(n_components=10)
X_train_reduced = pca.fit_transform(X_train)  # Learn from train only
X_test_reduced = pca.transform(X_test)  # Apply train-learned transformation
```

**Pattern 4: Target Encoding with Full Dataset**
```python
# ❌ WRONG: Uses target values from test set
category_means = df.groupby('category')['target'].mean()  # Includes test targets
df['category_encoded'] = df['category'].map(category_means)
X_train, X_test, y_train, y_test = train_test_split(df, y)

# ❌ ALSO WRONG (self-leakage): train-global means mapped onto the same
# training rows — every row's own target feeds its own feature
X_train, X_test, y_train, y_test = train_test_split(df, y)
train_df = X_train.copy()
train_df['target'] = y_train
category_means = train_df.groupby('category')['target'].mean()
X_train['category_encoded'] = X_train['category'].map(category_means)

# ✅ CORRECT: out-of-fold (OOF) encodings for training rows,
# train-global means for test rows
from sklearn.model_selection import KFold

X_train, X_test, y_train, y_test = train_test_split(df, y)
train_df = X_train.copy()
train_df['target'] = y_train
global_mean = y_train.mean()

# Each training row is encoded by a mean fit on the OTHER folds only,
# so no row's own target leaks into its feature
oof = pd.Series(index=train_df.index, dtype=float)
kf = KFold(n_splits=5, shuffle=True, random_state=42)
for tr_idx, val_idx in kf.split(train_df):
    means = train_df.iloc[tr_idx].groupby('category')['target'].mean()
    oof.iloc[val_idx] = train_df.iloc[val_idx]['category'].map(means)

X_train = X_train.copy()
X_test = X_test.copy()
X_train['category_encoded'] = oof.fillna(global_mean)  # unseen category → global mean

# Test rows: map fitted on ALL training targets (test labels stay unknown)
category_means = train_df.groupby('category')['target'].mean()
X_test['category_encoded'] = X_test['category'].map(category_means).fillna(global_mean)
```
Equivalent alternatives for training rows: leave-one-out encodings
(`(category_sum - y_i) / (category_count - 1)`) or smoothed/weight-of-evidence
encodings. The rule is the same: never encode a training row with a statistic
that includes that row's own target.

**Pattern 5: Feature Selection on Full Dataset**
```python
# ❌ WRONG: Feature selection sees test set
from sklearn.feature_selection import SelectKBest
selector = SelectKBest(k=10)
X_selected = selector.fit_transform(X, y)  # Uses test set for selection
X_train, X_test, y_train, y_test = train_test_split(X_selected, y)

# ✅ CORRECT: Select features using training data only
X_train, X_test, y_train, y_test = train_test_split(X, y)
selector = SelectKBest(k=10)
X_train_selected = selector.fit_transform(X_train, y_train)  # Train only
X_test_selected = selector.transform(X_test)  # Apply train-learned selection
```

**Pattern 6: Random Split on Temporal Data**
```python
# ❌ WRONG: Random split on time series (uses future to predict past)
X_train, X_test = train_test_split(df, test_size=0.2, random_state=42)

# ✅ CORRECT: Time-based split for temporal data
split_date = '2024-01-01'
X_train = df[df['date'] < split_date]
X_test = df[df['date'] >= split_date]
```

**Pattern 7: Future Function in Time Series Features**
```python
# ❌ WRONG: Uses future data to compute current features
df['daily_avg'] = df.groupby('date')['value'].transform('mean')  # Includes all day's data

# ✅ CORRECT: Use only past data (expanding window)
df = df.sort_values(['user_id', 'timestamp'])
df['cumulative_avg'] = (
    df.groupby('user_id')['value'].expanding().mean()
      .reset_index(level=0, drop=True)
)
# For a next-step prediction, shift before rolling/expanding so the
# current observation is not included in its own feature.
df['prior_30_avg'] = (
    df.groupby('user_id')['value'].shift(1)
      .groupby(df['user_id']).rolling(30, min_periods=1).mean()
      .reset_index(level=0, drop=True)
)
```

**Pattern 8: Post-Event Features**
```python
# ❌ WRONG: Feature only exists after the outcome
# Predicting loan default using "number of collection calls" as feature
# Collection calls only happen AFTER default occurs

# ✅ CORRECT: Use only pre-event features
# Use features available BEFORE the outcome: credit score, income, debt ratio, etc.
```

**Pattern 9: Leakage in Cross-Validation**
```python
# ❌ WRONG: Preprocessing before CV split
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
scores = cross_val_score(model, X_scaled, y, cv=5)  # Each fold sees other folds' statistics

# ✅ CORRECT: Preprocessing inside CV pipeline
from sklearn.pipeline import Pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LogisticRegression())
])
scores = cross_val_score(pipeline, X, y, cv=5)  # Scaling happens per fold
```

**Pattern 10: Data Augmentation Leakage**
```python
# ❌ WRONG: Augment before split (test set influenced by augmented train data)
X_augmented = augment_data(X)  # Augmentation sees all data
X_train, X_test, y_train, y_test = train_test_split(X_augmented, y)

# ✅ CORRECT: Augment only training data after split
X_train, X_test, y_train, y_test = train_test_split(X, y)
X_train_augmented = augment_data(X_train)  # Augment train only
# X_test remains unchanged
```

### Leakage Detection Checklist

After any ML preprocessing or feature engineering, verify:

1. **Fit-Transform Order**: Did I fit any transformer (scaler, encoder, imputer, PCA) on the full dataset before splitting?
2. **Global Statistics**: Did I compute any statistics (mean, std, median, mode) using the entire dataset?
3. **Feature Selection**: Did I select features using information from the test set?
4. **Target Information**: Did any feature encoding use target values from the test set?
5. **Temporal Order**: For time series, did I use random splits or include future information?
6. **Post-Event Features**: Are any features only available after the outcome occurs?
7. **Cross-Validation**: Did I preprocess before setting up CV folds?
8. **Production Reality**: At prediction time, can I actually compute this feature with available data?

### The "Prediction Time" Test

For every feature and preprocessing step, ask:

```
When the model is deployed and receives a new data point at time T:
- Can I query this value from the database?
- Can I compute this statistic using only data available before time T?
- Does this feature require knowing the outcome I'm trying to predict?

If any answer is "NO", you have data leakage.
```

## Examples

### Example 1: Detecting Normalization Leakage

**Input**: Code that normalizes data before train-test split

```python
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_normalized = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_normalized, y, test_size=0.2)
```

**Leakage Detection**:
- ❌ **LEAKAGE DETECTED**: `fit_transform` on entire dataset X
- The scaler learned mean and std from the full dataset, including test set
- At prediction time, you won't have access to test set statistics
- Test set performance is artificially inflated

**Corrected Code**:
```python
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
scaler = StandardScaler()
X_train_normalized = scaler.fit_transform(X_train)  # Fit on train only
X_test_normalized = scaler.transform(X_test)  # Transform using train statistics
```

### Example 2: Detecting Missing Value Imputation Leakage

**Input**: Code that fills missing values with global mean

```python
df = pd.read_csv('data.csv')
df['income'] = df['income'].fillna(df['income'].mean())  # (assign; inplace on a Series is a CoW no-op)
X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=0.2)
```

**Leakage Detection**:
- ❌ **LEAKAGE DETECTED**: Global mean computed on entire dataset
- The mean includes test set values
- At prediction time, you won't know the test set mean
- This inflates test performance

**Corrected Code**:
```python
df = pd.read_csv('data.csv')
X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=0.2)
train_mean = X_train['income'].mean()  # Compute mean from training data only
X_train['income'] = X_train['income'].fillna(train_mean)
X_test['income'] = X_test['income'].fillna(train_mean)  # Use training mean for test
```

### Example 3: Detecting Time Series Leakage

**Input**: Stock price prediction with random split and rolling average feature

```python
df['rolling_avg_7d'] = df.groupby('stock')['price'].rolling(7, center=True).mean()
X_train, X_test = train_test_split(df, test_size=0.2, random_state=42)
```

**Leakage Detection**:
- ❌ **LEAKAGE DETECTED - Multiple Issues**:
  1. `center=True` in rolling window uses future prices (t+3 days) to compute feature at time t
  2. Random split on temporal data means using "tomorrow's data" to predict "yesterday"
  3. At prediction time, you can't access future prices

**Corrected Code**:
```python
# Fix 1: Backward-looking window that EXCLUDES the current row.
# Rule: rolling() includes the current row; when the label is at time t
# (or earlier), shift(1)+ — i.e. shift by at least the prediction horizon —
# before rolling so the row's own label never enters its feature.
df = df.sort_values(['stock', 'date'])
df['rolling_avg_7d'] = df.groupby('stock')['price'].transform(
    lambda s: s.shift(1).rolling(7, min_periods=1).mean()
)

# Fix 2: Time-based split instead of random
split_date = '2024-01-01'
X_train = df[df['date'] < split_date]
X_test = df[df['date'] >= split_date]
```

### Example 4: Detecting Target Encoding Leakage

**Input**: Category encoding using target mean from full dataset

```python
category_target_mean = df.groupby('category')['target'].mean()
df['category_encoded'] = df['category'].map(category_target_mean)
X_train, X_test, y_train, y_test = train_test_split(df.drop('target', axis=1), df['target'])
```

**Leakage Detection**:
- ❌ **LEAKAGE DETECTED**: Target encoding uses test set labels
- The encoding directly uses the answer (target) from test set
- This is severe leakage - you're literally using test labels as features
- At prediction time, you don't know the target value

**Corrected Code**:
```python
from sklearn.model_selection import KFold

X_train, X_test, y_train, y_test = train_test_split(df.drop('target', axis=1), df['target'])
train_df = X_train.copy()
train_df['target'] = y_train
global_mean = y_train.mean()

# OOF encodings for training rows: each row's mean comes from the OTHER
# folds only, so its own target never enters its own feature
oof = pd.Series(index=train_df.index, dtype=float)
kf = KFold(n_splits=5, shuffle=True, random_state=42)
for tr_idx, val_idx in kf.split(train_df):
    means = train_df.iloc[tr_idx].groupby('category')['target'].mean()
    oof.iloc[val_idx] = train_df.iloc[val_idx]['category'].map(means)

X_train['category_encoded'] = oof.fillna(global_mean)

# Test rows: mean over ALL training targets only
category_target_mean = train_df.groupby('category')['target'].mean()
X_test['category_encoded'] = X_test['category'].map(category_target_mean).fillna(global_mean)
```

### Example 5: Detecting Post-Event Feature Leakage

**Input**: Predicting customer churn using "number of retention calls" as feature

```python
features = ['account_age', 'monthly_spend', 'support_tickets', 'retention_calls_count']
X = df[features]
y = df['churned']
```

**Leakage Detection**:
- ❌ **LEAKAGE DETECTED**: Post-event feature
- "retention_calls_count" only exists AFTER customer shows churn signals
- Company only makes retention calls to customers who are already churning
- This is a consequence of churn, not a predictor
- At prediction time (before churn), this feature doesn't exist or is always 0

**Corrected Code**:
```python
# Remove post-event features, use only pre-event features
features = ['account_age', 'monthly_spend', 'support_tickets', 'login_frequency',
            'feature_usage_decline', 'payment_delays']
X = df[features]
y = df['churned']
```

## Leakage Severity Levels

**CRITICAL** (Model is completely invalid):
- Target encoding with test labels
- Post-event features
- Using future data in time series

**HIGH** (Significantly inflated performance):
- Preprocessing before train-test split
- Feature selection on full dataset
- Global imputation statistics

**MEDIUM** (Moderate performance inflation):
- Incorrect cross-validation setup
- Subtle temporal leakage in feature engineering

## References

- `references/leakage-patterns.md`: Comprehensive catalog of leakage patterns
- `references/temporal-leakage.md`: Time series specific leakage issues
- `references/detection-strategies.md`: How to detect leakage in existing code

## Maintenance

- Sources: ML best practices, Kaggle competition lessons, production ML experience
- Last updated: 2026-01-19
- Known limits: Cannot detect domain-specific leakage without context (e.g., whether a feature is post-event in a specific business context)

## Hermes adaptation

This is an adapted, on-demand Hermes skill. Use the existing project environment and installed dependencies; do not install packages or contact external services automatically. Supporting files are relative to `${HERMES_SKILL_DIR}`.

## Provenance

Adapted from [https://github.com/foryourhealth111-pixel/Vibe-Skills](https://github.com/foryourhealth111-pixel/Vibe-Skills) at commit `ddcaa2affca93c1efe026d008b6b93709e5fb7e2`. Upstream repository license: Apache-2.0. The source file declares no separate license; the repository Apache-2.0 notice is retained in the source mirror.
