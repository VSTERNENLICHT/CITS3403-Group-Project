# CITS3403 Group Project
Group Code: Group_gc_29

## Group Members
| UWA ID |     Name     |  GitHub User Name  |
|--------|--------------|--------------------|
|23778874|Brian Chan    |BrianC-04           |
|24476802|Norbu Tshering|norbu13             |
|23902644|Seoyoung Park |VSTERNENLICHT       |
|22974298|Max Bennett   |Max-Bennett-22974298|

## Description 
**CalcMyWAM** is a web application designed to help university students easily track and manage their academic progress. Whether you're aiming for a scholarship, graduation with distinction, or just want to stay on top of your studies, CalcMyWAM gives you the tools to calculate your WAM (Weighted Average Mark) and GPA in a simple, visual, and goal-oriented way.

## Features
- Set your desired WAM or GPA goal  
- Enter unit results to calculate your current WAM and GPA  
- View progress graphs semester by semester  
- Compare your results with your goals  
- Share unit plans and performance with friends

## Set up
1. Download and unzip the zip file
2. Open terminal at folder
3. Create a virtual environment using: `python3 -m venv venv`
4. Activate the virtual environment using: `source venv/bin/activate`
5. Install required packages from requirements.txt using: `pip install -r requirements.txt`
6. Run the application using: `flask run` (Note: This may take some time as some modules may take a while loading the first time)

## Testing
Test files are located in `/tests`.

### Unit Tests
1. Sign-up Page
2. Login Page
3. Calculator Page: Use command `python -m unittest tests.test_calculator`
4. Set Goal Page: Use command `python -m unittest tests.test_set_goal`
5. Share Page: Use command `python -m unittest tests.test_share_routes`

### System Tests
