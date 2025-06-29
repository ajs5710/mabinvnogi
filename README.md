# mabinvnogi
Attempt to locate and visualize items (focused around dyes) across pets inventories in Mabinogi



### QuickStart aka Skip the Rest of the Page
You can use the csv version of the page here: https://mabinogi-dyes.timreks.tools/

It uses my list of dyes by default but can have a url to a csv pasted in to override it.

The csv is expected to be as follows:
```
Color,Type of Dye,Pet Name
#RRGGBB,Fixed Dye Ampoule,dyeperbaby
```
Of those columns only Color is really important.  The other two columns could be other things that make logical sense to you instead. For example, "Bank Tab" might make more sense to you than "Pet Name" depending on where you are storing your dyes.

Only the first three Columns are used by the page and additional columns can be tracked in your csv to help with record-keeping.  Note that any additional columns in that tab will be visible to anyone you share the link with. 

**DO NOT USE COMMAS OR NEW LINE CHARACTERS IN THE CSV**.  The parsing of the CSV that is being done is pretty naive and will likely not work correctly if it encounters an extra comma or return.

Here is an example sheet for reference: https://docs.google.com/spreadsheets/d/1mfMIGsd6peQfKsz48x7d8Zk98zftMxba47E2uLYWpd0/edit?usp=sharing I recommend using a google sheet as it makes it pretty easy to publish the CSV so that you can paste the link into The Visualizer.
Refer to the csvguide.html page for a little more details on publishing a tab in a google sheet.







**This project is broken up into three main parts:**

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

Note that there are multiple tunnels in the Ngrok configuration.  One of these tunnels will only return the "fromcsv.html" page.  The idea behind this is that there are no questions about tos for this page.


### Some Notes About Sharing
The 'fromcsv.html' file is setup to be sourced from a csv file.  This accomplishes two things.  Firstly, it makes it possible to allow others to use The Visualizer relatively easily based on a manually created csv file.  Secondly, using this version obfuscates the data generation methods, which while maybe not strictly necessary, might run slightly afoul of the TOS.

The downside is that the 'fromcsv.html' and by extension the 'safe' ngrok tunnel do not include the unidentified (i.e. flashy) dyes.
