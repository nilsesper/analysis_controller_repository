
BASE_DIR="analyis_controller_repository/"
SCRIPT_PATH="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/$(basename -- "${BASH_SOURCE[0]}")"
RELATIVE_SCRIPT_PATH="${SCRIPT_PATH#*/analysis_controller_repository/}"

echo "script_path = $SCRIPT_PATH"
echo "base_path = $BASE_DIR"

echo "==> relative_script_path = $RELATIVE_SCRIPT_PATH"
