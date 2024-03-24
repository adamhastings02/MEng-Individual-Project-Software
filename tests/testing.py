text = "Your original text"
words_with_locations = [('parathyroid', 11, 22), ('parathyroid', 12, 23), ('lesion', 28, 34)]

true_text = "The true text corresponding to the original text with parathyroid and lesion added"
updated_words_with_locations = []

# Iterate through each word and its locations
for word, start, end in words_with_locations:
    # Find the true start and end locations of the word in the true text
    true_start = true_text.find(word)
    true_end = true_start + len(word)

    # Update the start and end locations with the true locations
    updated_words_with_locations.append((word, true_start, true_end))

# Print the updated words with their true locations
print(updated_words_with_locations)
