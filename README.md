# Time Tracker

A Qt-Application to start and stop time tracking, enter additional breaks, view your daily and monthly data, and generate a report out of it.

![mainwindow](./doc/mainwindow.PNG 'mainwindow')
![report](./doc/report.PNG 'report')

## Installation

### A: Standalone Installation

With a new release, there is also a standalone version available.
You can download the latest release from the [release page](https://github.com/AndreWohnsland/TimeTracker/releases).
Choose the right version for your operating system and download the file.
Execute the file according to your usual system start option.
The application will start and you can use it as described below.

#### Windows

Just use the installer, put it on the desktop, and start the application via the icon.

#### Linux

You probably know your ways how to get started with the binary file.
But if you are lazy like me, you can install the application with the [following script](https://github.com/AndreWohnsland/TimeTracker/blob/master/scripts/installer.sh):

```bash
curl -s https://raw.githubusercontent.com/AndreWohnsland/TimeTracker/master/scripts/installer.sh | bash
```

This will download the latest release, put it into your binary folder, and create an application entry.

### B: Manual Installation

This application needs at least Python 3.8 installed at the system as well as the required packages.
First clone the repository and cd into it.
The required package can be installed with pip.
To start the app, you run the `runme.py` file with python, you can create a shortcut on your desktop:

```bash
git clone https://github.com/AndreWohnsland/TimeTracker.git
cd TimeTracker
pip install -r requirements.txt
python runme.py
```

## Options

On first startup, the application will create the needed configuration and the database.
You can adjust your settings via `Options > Configure Settings` and the folder to save the reports to with `Options > Set Save folder`.
With `Start` the tracking is started and with `Stop` the tracking is stopped.
You can repeat this start-stop procedure any time you want.
Over the spin box you can select the pause time and submit them with the `Pause` button.
It is also possible to enter negative Pause to correct previous mistakes.
You can also start and stop over the tray icon in the taskbar.

![settings](./doc/options.PNG 'settings')

## Reports

An overview can be seen when clicking `Options > Summary`.
With a datepicker, a day can be chosen to display a summary of the data in either the according month or all events of this day.
The day / month view can be changed over the view toggle button.
To generate the report of your overtime or work time, click the `Export` button.
By default settings, the report will be saved into the reports folder of this application.
As soon as the save folder was changed over the option setting, the app will use this location instead.
The default work time for overtime is eight hours, time worked less than eight will displayed as zero overtime.
The overtime/work time is rounded to the closest quarter hour.
Breaks are already subtracted in the calculation, adherence to the regular break times is not observed.

## Adjust Past Values

To enter values you have missed, you can switch to past entry mode.
This can be done over the `Options > Switch to Past Entry` setting.
A date and time can be selected with the according action to insert past values.
To go back to the default option, click the shown back button.

## Updating to latest Version

INFO: Latest version should just be downloaded and installed over the previous version.
If updating from version v1.0 you need to go into the directory and run:

```bash
git pull
pip install -r requirements.txt
```

Since version v1.1 it is also possible to update over the UI with `Options > Search for Updates`.
The app will need to be restarted to apply changes.
You can also just download the latest executable from the [release page](https://github.com/AndreWohnsland/TimeTracker/releases).

## ToDo's

- Implement a proper update logic to only use latest releases
