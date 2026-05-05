#!/data/data/com.termux/files/usr/bin/python

import os
import matplotlib.pyplot as plt

current_dir = os.getcwd()

subdir_sizes = {}
total_size = 0

for dirpath, dirnames, filenames in os.walk(current_dir):
    dir_size = 0
    for f in filenames:
        fp = os.path.join(dirpath, f)
        # Avoid errors due to symbolic links or permissions
        try:
            dir_size += os.path.getsize(fp)
        except OSError:
            pass

    # If it's a subdirectory (not the root), add its size to the total
    # We check if dirpath is not equal to current_dir to exclude the root's own size calculation for now
    if dirpath != current_dir:
        subdir_sizes[dirpath] = dir_size
        total_size += dir_size
    else:
        # For the root directory, we still need to add its files' sizes to total_size
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total_size += os.path.getsize(fp)
            except OSError:
                pass


# Calculate percentages
subdir_percentages = {}
for subdir, size in subdir_sizes.items():
    # Avoid division by zero if total_size is 0
    if total_size > 0:
        percentage = (size / total_size) * 100
        # Get the last part of the directory name for cleaner labels
        subdir_percentages[os.path.basename(subdir)] = percentage
    else:
        subdir_percentages[os.path.basename(subdir)] = 0

# Prepare labels and sizes for the pie chart
labels = list(subdir_percentages.keys())
sizes = list(subdir_percentages.values())

reshaped_labels = []
for label in labels:
    reshaped_labels.append(label)

fig, ax = plt.subplots(figsize=(10, 10))
ax.pie(sizes, labels=reshaped_labels, autopct="%1.1f%%beding", startangle=140)
ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.

# Add a title in Persian
title = "subdirs sizes"
plt.title(title)

# Save the plot to a file
output_filename = "size.png"
plt.savefig(output_filename, bbox_inches="tight")

print(f"saved '{output_filename}'")
print(f"size: {total_size}")
