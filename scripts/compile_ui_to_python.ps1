cd .\ui\

$files = @(
  "mainwindow", "config_window", "plot_window",
  "vacation_window"
)

foreach ($f in $files) {
  pyuic5 -x .\$f.ui -o .\$f.py
}

cd ..