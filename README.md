# SDSS_SpecViewer
authors: Dr. Jennifer Li (UIUC) and Meg Davis (UConn, megan.c.davis@uconn.edu), 2021

---
# Getting Started

### Authentication

You **must** edit the `authentication.txt` before running with the proper SDSS-V Proprietary Data username and password before running the tool. Please ensure that there are NO extra spaces after the username or password (just hit enter after the last character you type for the username). The code will immediately check the authentication upon start up. 

### Dependencies
Please install the following Python packages to use this tool. The provided "dependencies.sh" shell script will pip install these for you, if you run it with: `./dependencies.sh`.
-  dash
-  plotly
-  astropy
-  requests
-  numpy
