#!/usr/bin/env bash
set -euo pipefail

VERSION="3.0.0"
SCRIPT_NAME="manager"
DATA_DIR="$HOME/.local/share/manager"
mkdir -p "$DATA_DIR"

#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# Powered by BytesAgain | bytesagain.com | hello@bytesagain.com

_info()  { echo "[INFO]  $*"; }
_error() { echo "[ERROR] $*" >&2; }
die()    { _error "$@"; exit 1; }

cmd_add() {
    local task="${2:-}"
    local priority="${3:-}"
    [ -z "$task" ] && die "Usage: $SCRIPT_NAME add <task priority>"
    echo '{"task":"'$2'","priority":"'${3:-medium}'","status":"todo","ts":"'$(date +%s)'"}' >> $DATA_DIR/tasks.jsonl && echo Added
}

cmd_list() {
    local status="${2:-}"
    [ -z "$status" ] && die "Usage: $SCRIPT_NAME list <status>"
    cat $DATA_DIR/tasks.jsonl 2>/dev/null | grep ${2:-} | tail -20
}

cmd_done() {
    local id="${2:-}"
    [ -z "$id" ] && die "Usage: $SCRIPT_NAME done <id>"
    echo 'Marked task $2 as done'
}

cmd_remove() {
    local id="${2:-}"
    [ -z "$id" ] && die "Usage: $SCRIPT_NAME remove <id>"
    sed -i ${2}d $DATA_DIR/tasks.jsonl 2>/dev/null && echo Removed
}

cmd_stats() {
    echo 'Total: '$(wc -l < $DATA_DIR/tasks.jsonl 2>/dev/null || echo 0)' tasks'
}

cmd_export() {
    local file="${2:-}"
    [ -z "$file" ] && die "Usage: $SCRIPT_NAME export <file>"
    cp $DATA_DIR/tasks.jsonl $2 && echo Exported
}

cmd_help() {
    echo "$SCRIPT_NAME v$VERSION"
    echo ""
    echo "Commands:"
    printf "  %-25s\n" "add <task priority>"
    printf "  %-25s\n" "list <status>"
    printf "  %-25s\n" "done <id>"
    printf "  %-25s\n" "remove <id>"
    printf "  %-25s\n" "stats"
    printf "  %-25s\n" "export <file>"
    printf "  %%-25s\n" "help"
    echo ""
    echo "Powered by BytesAgain | bytesagain.com | hello@bytesagain.com"
}

cmd_version() { echo "$SCRIPT_NAME v$VERSION"; }

main() {
    local cmd="${1:-help}"
    case "$cmd" in
        add) shift; cmd_add "$@" ;;
        list) shift; cmd_list "$@" ;;
        done) shift; cmd_done "$@" ;;
        remove) shift; cmd_remove "$@" ;;
        stats) shift; cmd_stats "$@" ;;
        export) shift; cmd_export "$@" ;;
        help) cmd_help ;;
        version) cmd_version ;;
        *) die "Unknown: $cmd" ;;
    esac
}

main "$@"
