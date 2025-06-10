import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

def generate_ckd_dataset_summary(data_path, output_dir):
    """
    Generates detailed visual summaries of the CKD dataset for documentation.
    """
    df = pd.read_csv(data_path)
    target_col = "Chronic Kidney Disease: yes"

    os.makedirs(output_dir, exist_ok=True)

    # --- Figure 3.1: Class Distribution ---
    plt.figure(figsize=(6, 4))
    class_counts = df[target_col].value_counts()
    labels = ["CKD", "No CKD"]
    ax = sns.barplot(x=labels, y=class_counts.values, palette="Set2")
    for i, v in enumerate(class_counts.values):
        ax.text(i, v + 3, str(v), ha='center', va='bottom', fontweight='bold')
    plt.title("Class Distribution in CKD Dataset")
    plt.ylabel("Number of Instances")
    plt.xlabel("Diagnosis")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig3_1_class_distribution.png"))
    plt.close()

    # --- Figure 3.2: Numerical vs Categorical Attributes ---
    numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=['number']).columns.tolist()
    num_numerical = len(numerical_cols)
    num_categorical = len(categorical_cols)

    plt.figure(figsize=(5, 5))
    plt.pie(
        [num_numerical, num_categorical],
        labels=['Numerical Attributes', 'Categorical Attributes'],
        autopct='%1.1f%%',
        colors=['#8fcbbc', '#f5c396'],
        startangle=140,
        explode=(0.05, 0.05)
    )
    plt.title("Proportion of Numerical vs Categorical Attributes")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig3_2_attribute_type_pie_chart.png"))
    plt.close()

    # --- Figure 3.3: Categorical Feature Distributions ---
    cat_features = categorical_cols.copy()
    if target_col not in cat_features:
        cat_features.append(target_col)

    for col in cat_features:
        plt.figure(figsize=(8, 4))
        sns.countplot(data=df, x=col, palette="Set3", order=df[col].value_counts().index)
        plt.title(f"Distribution of {col}")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        filename = f"fig3_3_categorical_{col.replace(' ', '_').replace(':', '')}.png"
        plt.savefig(os.path.join(output_dir, filename))
        plt.close()

    # --- Figure 3.4: Heatmap of Numerical Feature Correlation ---
    heatmap_df = df[numerical_cols].dropna()
    corr = heatmap_df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", mask=mask, linewidths=0.5)
    plt.title("Correlation Heatmap of Numerical Features")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig3_4_numerical_correlation_heatmap.png"))
    plt.close()

    # --- Figure 3.5: Pairplot of Numerical Features (top 5 correlated only) ---
    top_corr = corr.abs().sum().sort_values(ascending=False).head(5).index.tolist()
    sns.pairplot(df[top_corr + [target_col]].dropna(), hue=target_col, palette="Set2", diag_kind="kde")
    plt.savefig(os.path.join(output_dir, "fig3_5_pairplot_top_correlated.png"))
    plt.close()

    # --- Figure 3.6: Missing Data Heatmap ---
    plt.figure(figsize=(12, 6))
    sns.heatmap(df.isnull(), cbar=False, cmap="YlGnBu")
    plt.title("Missing Data Heatmap")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "fig3_6_missing_data_heatmap.png"))
    plt.close()

    # --- Summary Table ---
    summary_table = pd.DataFrame({
        "Total Instances": [df.shape[0]],
        "Total Attributes": [df.shape[1]],
        "Numerical Attributes": [num_numerical],
        "Categorical Attributes": [num_categorical],
        "CKD Cases": [class_counts.get(1, 0)],
        "Non-CKD Cases": [class_counts.get(0, 0)]
    })

    fig, ax = plt.subplots(figsize=(8, 1.5))
    ax.axis('off')
    table = ax.table(
        cellText=summary_table.values,
        colLabels=summary_table.columns,
        loc='center',
        cellLoc='center'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.5)
    plt.savefig(os.path.join(output_dir, "fig3_7_dataset_summary_table.png"))
    plt.close()

    print("[INFO] All rich visualizations generated successfully for documentation.")

if __name__ == "__main__":
    data_path = r"C:\Users\USER\Documents\GitHub\Multi-Disease-Diagnosis-System-v0\backend\dataset\CKD\CKD_Preprocessed.csv"
    output_dir = r"C:\Users\USER\Documents\GitHub\Multi-Disease-Diagnosis-System-v0\backend\scripts\ckd_scripts\img\doc_visuals"
    generate_ckd_dataset_summary(data_path, output_dir)
