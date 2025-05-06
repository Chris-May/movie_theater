#!/usr/bin/env just --justfile
export PATH := join(justfile_directory(), ".env", "bin") + ":" + env_var('PATH')

upgrade:
  uv lock --upgrade

watch-css:
  #!/usr/bin/env bash
  set -euxo pipefail
  cd src/movie/web/static
  npx @tailwindcss/cli -i _build/css/init.css -o css/app.css --watch
