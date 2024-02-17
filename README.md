# KDMID Queue Checker Bot

Automatically checks the queue status after an appointment intent 

If you are in the queue waiting for a free slot for an appointment in the Russian consulate, you must check the status of the queue at least once a day, 
which means enter the page with your order number and code and see if free slots are available. Once you stop entering the page daily, 
they remove your order from the queue and you have to start the process once again. 

This bot is designed to make the iterative checking process automatic and get the first nearest timeslot. You can set a period to check. 
If success, you will get an email from the consulate with the information about your appointment and the success file will be written in the work folder. There is no option of selecting the slot, if there are various. 

If you don't like the time the bot got for you, you can cancel the appointment on the page (manually) and come back to the queue with the same order number and code. Don't forget to delete the success.txt file in the work directory before running the script, as it is written to stop iteration. 

## Requirements  

- *Tesseract* 

Tesseract OCR is used to recognize captcha digits. It should be installed on the machine. For Windows, see the installation instructons here https://github.com/UB-Mannheim/tesseract/wiki

- *Chrome*

- *Python 3.9* 

## Setup

1. **Set up the Conda environment:**
   - Install Miniconda by downloading the installer:
     - Download Miniconda installer with `wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh`.
     - Run the installer script with `bash Miniconda3-latest-Linux-x86_64.sh`.
   - Update the bash environment with `source ~/.bashrc`.
   - Create and activate a Conda environment named "kdmid_bot" with Python 3.9:
     - `conda create --name kdmid_bot python=3.9`
     - `conda activate kdmid_bot`.
   - Install project dependencies from `requirements.txt` using `pip install -r requirements.txt`.

2. **Setup chromedriver:**
   - Download chromedriver with `wget -N https://chromedriver.storage.googleapis.com/119.0.6045.105/chromedriver_linux64.zip -P ~/Downloads`.
   - Install unzip with `sudo apt install unzip`.
   - Unzip and move chromedriver to `/usr/local/bin/`:
     - `unzip ~/Downloads/chromedriver-linux64.zip -d /usr/local/bin/`
     - `chmod +x /usr/local/bin/chromedriver`.

3. **Install Tesseract OCR:**
   - Install Tesseract OCR with `sudo apt install tesseract-ocr`.
   - Verify Tesseract installation with `tesseract --version`.

4. **Ensure that chromedriver and Tesseract OCR are correctly installed and accessible in the system path for the project's execution.**

5. **Run the queue bot:**
   - Activate the Conda environment with `conda activate kdmid_bot`.
   - Launch the queue bot in the background:
     - `nohup python queue_bot.py --subdomain lisboa --order_code_pairs 54937,2E74DD83 --every_hours 2 > output.txt &`.


