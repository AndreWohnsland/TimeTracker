# Time Tracker

A Qt-Application to start and stop time tracking, enter additional breaks, view your daily and monthly data, and generate a report out of it.

![mainwindow](https://github.com/AndreWohnsland/TimeTracker/blob/master/doc/mainwindow.PNG 'mainwindow')
![report](https://github.com/AndreWohnsland/TimeTracker/blob/master/doc/report.PNG 'report')

# Installation

This application needs at least Python 3.6 installed at the system as well as the required packages. First clone the repository and cd into it. The required package can be installed with pip. To start the app, you run the `runme.py` file with python, you can create a shortcut on your desctop:

```
git clone https://github.com/AndreWohnsland/TimeTracker.git
cd TimeTracker
pip install -r requirements.txt
python runme.py
```

# Options

On first startup, the application will create the needed configuration and the database. You can adjust your settings via `Options > Configurate Settings` and the folder to save the reports to with `Options > Set Savefolder`. With `Start` the tracking is started and with `Stop`the tracking is stopped. You can repeat this start-stop procedure any time you want. Over the spin box you can select the pause time and submit them with the `Pause` button. It is also possible to enter negative Pause to correct previous mistakes.

# Reports

An overview can be seen when clicking `Options > Summary`. Over a datepicker, a day can be chosen to display a summary of the data in either the according month or all events of this day. The day / month view can be changed over the view togglebutton. To generate the report of your overtime, click the `Export` button. By default settings, the report will be saved into the reports folder of this application. As soon as the savefolder was changed over the option setting, the app will use this location instead. Only overtime is displayed. Time less than eight hours is displayed as zero. The overtime is rounded to the closest quarter hour.

# Adjust Past Values

In a future version there will be the possibility to adjust or add past values. This will be done over the `Options > Add Old Events` setting, which currently got no function. A date can be selected with the according action to insert past values.

# ToDo's

- Give the possibility to enter past values
- Give the possibility to adjust or at least delete old events after a confirmation prompt (over the report window)
