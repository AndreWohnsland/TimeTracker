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

An overview can be seen when clicking `Options > Summary`. With a datepicker, a day can be chosen to display a summary of the data in either the according month or all events of this day. The day / month view can be changed over the view togglebutton. To generate the report of your overtime or worktime, click the `Export` button. By default settings, the report will be saved into the reports folder of this application. As soon as the savefolder was changed over the option setting, the app will use this location instead. The default worktime for overtime is eight hours, time worked less than eight will displayed as zero overtime. The overtime/worktime is rounded to the closest quarter hour. Breaks are already subtracted in the calculation, adherence to the regular break times is not observed.

# Adjust Past Values

To enter values you have missed, you can switch to past entry mode. This can be done over the `Options > Switch to Past Entry` setting. A date can be selected with the according action to insert past values. To go back to the default option, click the shown back button.

# Updating to latest Version

If updating from version v1.0 you need to go into the directory and run:

```
git pull
pip install -r requirements.txt
```

Since version v1.1 it is also possible to update over the UI with `Options > Search for Updates`.

# ToDo's

- Give the possibility to adjust or at least delete old events after a confirmation prompt (over the report window)
- Implement a proper update logic to only use latest releases
