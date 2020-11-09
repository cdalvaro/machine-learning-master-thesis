#!/usr/bin/env bash

set -e

DOCKER_COMPOSE_FILE="$(dirname "$0")/../docker-compose.yml"
VOLUME_NAME="gaia-postgres-data"

BACKUP_DIR="$(pwd)"
BACKUP_DATE="$(date +%Y-%m-%d_%H%M%S)"

ERRORS_FOUND=false
STOP_SERVICES=true

BACKUP=false
RESTORE=false

function help() {
  echo "manage_db backup|restore|help"
  echo ""
  echo "  backup [OPTIONS]                       Create a new backup with the current timestamp"
  echo "    -d|--dest                            Destination directory for the backup file. Defaults to: ${BACKUP_DIR}"
  echo "    -v|--volume                          Docker volume to backup. Defaults to: ${VOLUME_NAME}"
  echo "    -s|--stop                            Stop container before creating backup. Defaults to: ${STOP_SERVICES}"
  echo "  restore YYYY-mm-dd_HHMMSS [OPTIONS]    Restore the especified backup"
  echo "    -s|--src                             Source directory of the backup file. Defaults to: ${BACKUP_DIR}"
  echo "    -v|--volume                          Docker volume to restore. Defaults to: ${VOLUME_NAME}"
  echo ""
  echo "  help                                   Show this message and exit"
  echo ""

  exit 2
}

function log_error() {
  (>&2 echo "$@")
}

case "${1}" in
backup)
  BACKUP=true
  shift
  while [[ $# -gt 0 ]]; do
    key="${1}"
    shift
    case "${key}" in
    -d | --dest)
      BACKUP_DIR="${1}"
      shift
      ;;
    -v | --volume)
      VOLUME_NAME="${1}"
      shift
      ;;
    -s | --stop)
      STOP_SERVICES="${2}"
      shift
      ;;
    *)
      log_error "Unknown parameter ${key}"
      help
      ;;
    esac
  done
  ;;
restore)
  RESTORE=true
  shift
  BACKUP_DATE="${1}"
  shift
  while [[ $# -gt 0 ]]; do
    key="${1}"
    shift
    case "${key}" in
    -s | --src)
      BACKUP_DIR="${1}"
      shift
      ;;
    -v | --volume)
      VOLUME_NAME="${1}"
      shift
      ;;
    *)
      log_error "Unknown parameter ${key}"
      help
      ;;
    esac
  done
  ;;
help | *)
  help
  ;;
esac

function __backup_volume() {
  local volume_name=$1
  local extension="${2:-gz}"
  local tar_file="${volume_name}-${BACKUP_DATE}.tar.${extension}"

  echo -n "Backing up volum ${volume_name} into ${tar_file} ..."
  docker run --rm \
    -v "${volume_name}":/volume:ro -v "${BACKUP_DIR}":/backup \
    loomchild/volume-backup backup -c "${extension}" "${tar_file}"

  test -f "${tar_file}" && chown "$(id -u)":"$(id -g)" "${tar_file}"
  if [[ $? -ne 0 ]]; then
    log_error "Failure"
    ERRORS_FOUND=true
  else
    echo "Success"
  fi
}

function __restore_volume() {
  local volume_name=$1
  local extension="${2:-gz}"
  local tar_file="${volume_name}-${BACKUP_DATE}"

  echo "Restoring volume ${volume_name} from ${tar_file} ..."
  docker run --rm \
    -v "${volume_name}":/volume -v "${BACKUP_DIR}":backup:ro \
    loomchild/volume-backup restore -c "${extension}" "${tar_file}"

  if [[ $? -ne 0 ]]; then
    log_error "Failed"
    ERRORS_FOUND=true
  fi
}

function backup() {
  # Stop services
  if [[ ${STOP_SERVICES} == true ]]; then
    echo "Stopping services ..."
    docker-compose --file "${DOCKER_COMPOSE_FILE}" down
  fi

  # Backup volume
  __backup_volume "${VOLUME_NAME}"

  # Start db service
  if [[ ${STOP_SERVICES} == true ]]; then
    echo "Starting db service ..."
    docker-compose --file "${DOCKER_COMPOSE_FILE}" up --detach db
  fi

  if [[ ${ERRORS_FOUND} == true ]]; then
    log_error "Errors found while backing up volume. Check log."
    exit 1
  fi
}

function restore() {
  # Remove service
  echo "Removing services and volumes ..."
  docker-compose --file "${DOCKER_COMPOSE_FILE}" down --volumes

  # Restoring volume
  __restore_volume "${VOLUME_NAME}"
  if [[ ${ERRORS_FOUND} == true ]]; then
    log_error "Errors found while restoring volume. Check log."
    exit 1
  fi

  # Start services
  echo "Starting db service ..."
  docker-compose --file "${DOCKER_COMPOSE_FILE}" up --detach db
}

## MAIN

if [[ ${EUID} -ne 0 ]]; then
  log_error "You must run this script with 'sudo' permissions to set the right owner for the backup file."
  exit 1
fi

[[ $BACKUP == true ]] && backup
[[ $RESTORE == true ]] && restore

exit 0
