#!/bin/bash
# Batch launch Claude Code sessions for code golf tasks
# Opens terminals for both baseline and CoMAP directories.
#
# Usage:
#   bash launch_tasks.sh                              # all 10 tasks × 2 dirs = 20 sessions
#   DIRS=baseline bash launch_tasks.sh                # baseline only
#   DIRS=comap bash launch_tasks.sh                   # CoMAP only
#   TASK_RANGE="1-5" bash launch_tasks.sh             # tasks 001-005 only
#   TERMINAL=iterm bash launch_tasks.sh               # use iTerm instead of Terminal.app

TASKS=("001" "002" "003" "004" "005" "006" "007" "008" "009" "010")

# Which directories to run — "both" (default), "baseline", or "comap"
RUN_DIRS=${DIRS:-"both"}

GOLF_DIR="/Users/jackson/Desktop/code-golf"
BASE_DIR="$GOLF_DIR/deepseek-v4-pro-baseline"
COMAP_DIR="$GOLF_DIR/deepseek-v4-pro-CoMAP"

TERMINAL=${TERMINAL:-"terminal"}  # "terminal" or "iterm"

PROMPT="read agent.md and start working. dont stop until you reached under 100 bytes, which is verified to be possible"

# Count total sessions
declare -a LAUNCH_LIST=()

for task in "${TASKS[@]}"; do
    if [ "$RUN_DIRS" = "both" ] || [ "$RUN_DIRS" = "baseline" ]; then
        LAUNCH_LIST+=("baseline|$task|$BASE_DIR/task$task")
    fi
    if [ "$RUN_DIRS" = "both" ] || [ "$RUN_DIRS" = "comap" ]; then
        LAUNCH_LIST+=("comap|$task|$COMAP_DIR/task$task")
    fi
done

echo "============================================"
echo " Code Golf Batch Launcher"
echo "============================================"
echo "Directories: $RUN_DIRS"
echo "Tasks:       ${TASKS[0]} → ${TASKS[-1]}"
echo "Sessions:    ${#LAUNCH_LIST[@]}"
echo "Terminal:    $TERMINAL"
echo "============================================"
echo

launch_terminal() {
    local label=$1
    local task=$2
    local dir=$3

    if [ ! -d "$dir" ]; then
        echo "  SKIP [$label] task$task: directory not found"
        return
    fi

    local title="[$label] task$task"
    local cmd="cd \"$dir\" && claude --dangerously-skip-permissions \"$PROMPT\""

    if [ "$TERMINAL" = "iterm" ]; then
        osascript -e "tell application \"iTerm\"
            tell current window
                create tab with default profile command \"$cmd\"
            end tell
        end tell" 2>/dev/null
    else
        osascript -e "tell application \"Terminal\"
            activate
            do script \"$cmd\"
        end tell" 2>/dev/null
    fi

    echo "  ✓  $title"
}

for entry in "${LAUNCH_LIST[@]}"; do
    IFS='|' read -r label task dir <<< "$entry"
    launch_terminal "$label" "$task" "$dir"
    sleep 2
done

echo
echo "Done. ${#LAUNCH_LIST[@]} sessions launched."
