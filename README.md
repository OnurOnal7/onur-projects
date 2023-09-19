# Onur Onal Projects
This repository serves as a display for two programming projects that I worked on this past year.

# ChefPort Backend
Chefport is a prototype website that myself and two other colleagues worked on this past semester.

It is a web application in which users can create, save and share food recipes.

My work on this project consisted of programming the server-side to user information into the database.

Key Backend Features:
- Creation of a REST API which passes data from controller to service to repository, and then into the database.
- "Sign-up" PostMapping method to create new users objects in the MongoDB Compass database with an HTTP POST requests.
- "Login" PostMapping method that displays boolean output based on whether a user with the inputted password exists in the database.
- GetMapping method to return existing users in the database.

# Oxygen Data Plotting with MATLAB 
As part of cold welding project in Aerospace Engineering deparment at Iowa State, 
I wrote a MATLAB program that plots a CSV file on oxygen data collected by our oxygen monitors.

Key Programmatic Features:
- Nested for loop to detect and fix jump spots in data collection.
- Use of the "semilogy" function that graphs logarithmically to clarify scale for exponential curve.
- Highlighting maximum and minimum points and creating vector to represent the average oxygen level.
