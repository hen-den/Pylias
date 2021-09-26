# Pylias
Automated download of all your files at Ilias-HHN.
## Description
Pylias is a Selenium based automation for the Ilias of Hochschule Heilbronn.

This tool downloads all your files from your courses without having to create directories on your own to manage the downloaded files. 

You can either specify a individual download-path or use the default download-directory within this project.
My advise would be to use a empty directory to begin with, because otherwise the files of the selected download-path 
will be moved to the newly created "content"-directory. This "content"-directory will be in your selected download-path.

## Installation

### 1. Install Chromedriver on your operating system:
**Windows:** Download the recent version of Chromedriver (https://sites.google.com/a/chromium.org/chromedriver/downloads)

**Linux / MacOS:** Execute the install.sh Bashscript in the terminal.
- Set execute permission on the script: `chmod +x install.sh`
- Navigate to the path of the script.
- To run the script, enter: `./install.sh`

### 2. Create Pipenv and install needed packages:
- Navigate to the project directory.
- Create the pipenv with: `pipenv install`
- Start pipenv with: `pipenv shell`
- To stop pipenv use: `exit`

## Usage
- Either download to project-path: `python main.py iliasname`
- or download to individual Path: `python main.py iliasname -p "enter//your//path//here"`
- Your password will be asked after this command and will be used to login into Ilias HHN.
Your Ilias **password is not stored** localy therefore it will be deleted after you finish the script.
