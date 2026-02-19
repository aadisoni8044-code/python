import pandas as pd

# Step 1: Create data
data = {
    "Name": ["Ram", "Shyam", "Mohan", "Sita", "Gita", "Ravi"],
    "Age": [15, 16, 14, 15, 16, 15],
    "Class": [9, 10, 8, 9, 10, 9],
    "Marks": [78, 85, 67, 90, 88, 72]
}

# Step 2: Create DataFrame
df = pd.DataFrame(data)

print("Full Data:")
print(df)

# Step 3: Show first 3 rows
print("\nFirst 3 Students:")
print(df.head(3))

# Step 4: Filter students with marks greater than 75
high_marks = df[df["Marks"] > 75]
print("\nStudents with Marks > 75:")
print(high_marks)

# Step 5: Add Result column
df["Result"] = df["Marks"].apply(lambda x: "Pass" if x >= 33 else "Fail")

print("\nData with Result Column:")
print(df)

# Step 6: Calculate average marks
average_marks = df["Marks"].mean()
print("\nAverage Marks:", average_marks)

# Step 7: Sort by Marks (descending)
sorted_df = df.sort_values(by="Marks", ascending=False)

print("\nSorted by Marks (High to Low):")
print(sorted_df)

# Step 8: Save data to CSV file
df.to_csv("student_data.csv", index=False)

print("\nData saved to student_data.csv successfully")



