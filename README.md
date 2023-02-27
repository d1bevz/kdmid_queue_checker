# KDMID Queue Checker Bot

Automatically checks the queue status after an appointment intent 

If you are in the queue waiting for a free slot for an appointment in the Russian consulate, you must check the status of the queue at least once a day, 
which means enter the page with your order number and code and see if free slots are available. Once you stop entering the page daily, 
they remove your order from the queue and you have to start the process once again. 

This bot is designed to make the iterative checking process automatic and get the first nearest timeslot. You can set a period to check. 
If success, you will get an email from the consulate with the information about your appointment and the success file will be written in the work folder. There is no option of selecting the slot, if there are various. 

If you don't like the time the bot got for you, you can cancel the appointment on the page (manually) and come back to the queue with the same order number and code. Don't forget de delete the <>success.txt file in the work directory to run the script, as it is written to stop iteration. 

## Requirements  

- *Tesseract* 

Tesseract OCR is used to recognize captcha digits. It should be installed on the machine. For Windows, see the installation instructons here https://github.com/UB-Mannheim/tesseract/wiki

- *Chrome*

- *Python 3.9* 

## Run 

The script was depeloped and tested in Windows Anaconda environment for the consulate in Madrid

```
git clone https://github.com/ZotovaElena/kdmid_queue_checker.git
cd kdmid_queue_checker
```

- install requirements in conda or pip virtual environment 

- in _config.py_ file indicate the path to Tesseract

- execute the following command, where: 

*--subdomain* is the city of the consulate 

*--order_id* is the number of the order assigned when you applied for the appointment for the first time (номер заявки)

*--code* is the security code of the order (защитный код)

*--every_hours* how often the bot will repeat the check: minimal interval is 1 hour, default is 2 hours. 
It is not recommended to check the page too often not to generate suspisious behaviour. Usually every 2-3 hours is enough to get the appoinmtment during 24 hours. 


```
python queue_bot.py --subdomain madrid --order_id 123610 --code 7AE8EFCC --every_hours 3
```

- execute in background mode:

```
python queue_bot.py --subdomain madrid --order_id 123610 --code 7AE8EFCC --every_hours 3 > output.txt & 
```

The logs are saved in queue.log
After getting an appointment, a _success.txt_ file is written in the work directory. 

### TODO 

- Ubuntu server version with browser imitation 

- Option to send an email about existing appointments without taking any.

- User Interface

- Docker and cloud deployment
