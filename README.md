# mabinvnogi
Attempt to locate and visualize items across pets inventories in Mabinogi

This project is broken up into three main parts:

### The Data Scraper
Located in the datascraper folder, this project consists of the python "inventorypets.py" file.
Running this file like `py ./inventorypets.py` will attempt to interact with the mabinogi window to enumerate the pet list.
Taking pictures of pet inventories and attempting to capture tooltips for any noted items.
Generates an output folder called "pets" which will contain all the run info.
In order to open the pet inventory it is needed to bind the open pet inventory shortcut.
As-is the script expects this shortcut to be the "O" key (normally the clock).
Note that it's up to you to cleanup this folder (i.e. remove it) between runs.
Takes some notable amount of time per pet; roughly between 30s and 1minute. 

### The Data Analyzer
This is the build-data.rb script.  
Its job is to analyze and aggregate the data from the data scraper step in the "pets" folder and generate summary files as .json
To do this it uses tesseract ocr in order to attempt to analyze the tooltip captures.
This runs in a docker container and can be run like `docker run --rm -v "$(pwd):/stuff" $(docker build -q .) /stuff/build-data.rb`

### The Visualizer
This is the web portion of the project.  Its job is to help visualize the output from the project.
To do this it uses the data analyzer output files to display them in a webpage.
First you must copy the "ngrok.yml.example" file as "ngrok.yml" and replace the `<authtoken>` with your valid ngrok authtoken.
After that the nginx and ngrok containers can be started using the docker compose as `docker-compose up`.
Nginx is used to serve the files which are all static and it is configured to serve them as localhost:8080
Ngrok is used to tunnel the nginx server to some outside domain.  Visiting localhost:4040 will allow you to inspect traffic flowing through this tunnel and can be used to view the external url.


