cd .\ui\

$files = @(
  "data_widget", "mainwindow"
)

foreach ($f in $files) {
  pyuic5 -x .\$f.ui -o .\$f.py
}

cd ..