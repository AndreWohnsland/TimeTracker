cd .\ui\

$files = @(
  "mainwindow", "config_window", "data_window",
  "vacation_window"
)

foreach ($f in $files) {
  pyuic6 -x .\$f.ui -o .\$f.py
}

cd ..