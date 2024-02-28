# Learning_RegEx.py
#------------------------------------------------#
# By: Adam Hastings
# Date: 26th October 2023
# Module: ELEC5870M - MEng Individual Project
# Description:
#------------------------------------------------#
# A program which documents my learning of the 
# RegEx feature in Python
#------------------------------------------------#

# -----------------------------------------------#
# Section 1. Background Information
# -----------------------------------------------#
# A RegEx, or Regular Expression, is a sequence of characters that forms a search pattern.
# RegEx can be used to check if a string contains the specified search pattern.
# Python has a built-in package called re, which can be used to work with Regular Expressions.
# You start by importing the re module:

import re
txt = "The rain in Spain"

# -----------------------------------------------#
# Section 2. Functionalities
# -----------------------------------------------#
# FUNCTIONS:
# findall	Returns a list containing all matches
# search	Returns a Match object if there is a match anywhere in the string
# split		Returns a list where the string has been split at each match
# sub		Replaces one or many matches with a string

# METACHARACTERS:
# []	A set of characters							"[a-m]"	
# \	    Signals a special sequence (can also escape special characters)	"\d"	
# .	    Any character (except newline character)	"he..o"	
# ^	    Starts with									"^hello"	
# $	    Ends with									"planet$"	
# *	    Zero or more occurrences					"he.*o"	
# +	    One or more occurrences						"he.+o"	
# ?	    Zero or one occurrences						"he.?o"	
# {}	Exactly the specified number of occurrences	"he.{2}o"	
# |	    Either or									"falls|stays"	
# ()	Capture and group

# SPECIAL CHARACTERS:
# \A	Returns a match if the specified characters are at the beginning of the string	"\AThe"	
# \b	Returns a match where the specified characters are at the beginning or at the end of a word r"ain\b	
# \B	Returns a match where the specified characters are present, but NOT at the beginning (or at the end) of a word r"ain\B"	
# \d	Returns a match where the string contains digits (numbers from 0-9)	"\d"	
# \D	Returns a match where the string DOES NOT contain digits	"\D"	
# \s	Returns a match where the string contains a white space character	"\s"	
# \S	Returns a match where the string DOES NOT contain a white space character	"\S"	
# \w	Returns a match where the string contains any word characters (characters from a to Z, digits from 0-9, and the underscore _ character)	"\w"	
# \W	Returns a match where the string DOES NOT contain any word characters	"\W"	
# \Z	Returns a match if the specified characters are at the end of the string	"Spain\Z"

# SETS:
# [arn]		Returns a match where one of the specified characters (a, r, or n) is present	
# [a-n]		Returns a match for any lower case character, alphabetically between a and n	
# [^arn]	Returns a match for any character EXCEPT a, r, and n	
# [0123]	Returns a match where any of the specified digits (0, 1, 2, or 3) are present	
# [0-9]		Returns a match for any digit between 0 and 9	
# [0-5][0-9]Returns a match for any two-digit numbers from 00 and 59	
# [a-zA-Z]	Returns a match for any character alphabetically between a and z, lower case OR upper case	
# [+]		In sets, +, *, ., |, (), $,{} has no special meaning, so [+] means: return a match for any + character in the string

# -----------------------------------------------#
# Section 3. Examples
# -----------------------------------------------#

# Example 3.1 - The findall() function
# Example 3.1.1 - List with matches
x = re.findall("ai", txt)
print("3.1.1) Findall, ai", x)

# Example 3.1.2 - List with no matches
x = re.findall("France", txt)
print("3.1.2) Findall, France", x)

# Example 3.1.3 - Findall using sets
x = re.findall("[in]",txt)
print("3.1.3) Findall 'In' with sets", x)

# Example 3.2 - The search() function
# Example 3.2.1 - First white space character search
x = re.search("\s", txt)
print("\n3.2.1) Search for first white-space:", x.start())

# Example 3.2.2 - Finding a word
x = re.search("Spain", txt)
print("3.2.2) Search for Spain:", x.group())

# Example 3.2.3 - Not finding a word
x = re.search("France", txt)
print("3.2.3) Search for France:", x)

# Example 3.3 - The split() function
# Example 3.3.1 - Split at each white space character
x = re.split("\s", txt)
print("\n3.3.1) Split at each white space:", x)

# Example 3.3.2 - Split at first white space occurence
x = re.split("\s", txt, 1)
print("3.3.2) Split at first white space:", x)

# Example 3.3.3 - Split at word
x = re.split("rain", txt)
print("3.3.3) Split at rain:", x)

# Example 3.4 - The sub() function
# Example 3.4.1 - Replace white spaces with 9
x = re.sub("\s", "9", txt)
print("\n3.4.1) Replace white spaces with 9:", x)

# Example 3.4.2 - Replace first 2 white spaces with 9s
x = re.sub("\s", "9", txt, 2)
print("3.4.2) Replace first 2 white spaces with 9s:", x)

# Example 3.4.3 - Replace country name
x = re.sub("Spain", "France", txt)
print("3.4.3) Replace country name:", x)

# -----------------------------------------------#
# Section 4. Match Object
# -----------------------------------------------#
# The Match object has properties and methods used to retrieve information about the search, and the result:
# .span() returns a tuple containing the start-, and end positions of the match.
# .string returns the string passed into the function
# .group() returns the part of the string where there was a match

# Example 4.1 - Return an object
x = re.search("ai", txt)
print("\n4.1) Object:", x)

# Example 4.2 - Find start and end position of a word
x = re.search(r"\bS\w+", txt)
print("4.2) Start and end position of word starting with S: ", x.span())

# Example 4.3 - Return an object
x = re.search(r"\bS\w+", txt)
print("4.3) Original String:", x.string)

# Example 4.4 - Return an object
x = re.search(r"\bS\w+", txt)
print("4.4) Find the word beginning with S:", x.group())
print("\n")