#!/bin/bash
input=$(cat)

# Model
MODEL=$(echo "$input" | jq -r '.model.display_name')

# Context window percentage + progress bar
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
GREEN='\033[38;5;114m'; YELLOW='\033[38;5;179m'; RED='\033[38;5;167m'
CLAUDE='\033[91m'; GRAY='\033[38;5;242m'; SOFT='\033[38;5;250m'
BOLD='\033[1m'; RESET='\033[0m'

if [ "$PCT" -ge 90 ]; then BAR_COLOR="$RED"
elif [ "$PCT" -ge 70 ]; then BAR_COLOR="$YELLOW"
else BAR_COLOR="$GREEN"; fi

BAR_WIDTH=10
FILLED=$((PCT * BAR_WIDTH / 100))
EMPTY=$((BAR_WIDTH - FILLED))
BAR_ON=""; BAR_OFF=""
[ "$FILLED" -gt 0 ] && BAR_ON=$(printf "%${FILLED}s" | sed 's/ /━/g')
[ "$EMPTY" -gt 0 ] && BAR_OFF=$(printf "%${EMPTY}s" | sed 's/ /─/g')
BAR="${BAR_COLOR}${BAR_ON}${GRAY}${BAR_OFF}${RESET}"

# Usage stats
COST=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
COST_FMT=$(printf '$%.2f' "$COST")
DURATION_MS=$(echo "$input" | jq -r '.cost.total_duration_ms // 0')
TOTAL_SECS=$((DURATION_MS / 1000))
if [ "$TOTAL_SECS" -ge 3600 ]; then DUR="$((TOTAL_SECS / 3600))h$(printf '%02d' $((TOTAL_SECS % 3600 / 60)))m"
elif [ "$TOTAL_SECS" -ge 60 ]; then DUR="$((TOTAL_SECS / 60))m$(printf '%02d' $((TOTAL_SECS % 60)))s"
else DUR="${TOTAL_SECS}s"; fi
SESSION_ID=$(echo "$input" | jq -r '.session_id')

# Monthly cost accumulator
MONTHLY_CACHE="$HOME/.claude/.statusline-monthly-costs"
MONTHLY_LOCK="${MONTHLY_CACHE}.lockdir"
CURRENT_MONTH=$(date +%Y-%m)

# Update current session's cost atomically using mkdir lock (format: YYYY-MM session_id cost)
_retries=0
while ! mkdir "$MONTHLY_LOCK" 2>/dev/null; do
  _retries=$((_retries + 1))
  [ "$_retries" -ge 50 ] && { rm -rf "$MONTHLY_LOCK"; mkdir "$MONTHLY_LOCK" 2>/dev/null; break; }
  sleep 0.01
done
trap 'rm -rf "$MONTHLY_LOCK"' EXIT

if [ -f "$MONTHLY_CACHE" ]; then
  grep -v "$SESSION_ID" "$MONTHLY_CACHE" > "${MONTHLY_CACHE}.tmp" 2>/dev/null || true
  mv "${MONTHLY_CACHE}.tmp" "$MONTHLY_CACHE"
fi
echo "$CURRENT_MONTH $SESSION_ID $COST" >> "$MONTHLY_CACHE"

rm -rf "$MONTHLY_LOCK"
trap - EXIT

# Sum all costs for current month
MONTHLY_COST=$(awk -v month="$CURRENT_MONTH" '$1 == month { sum += $3 } END { printf "%.2f", sum }' "$MONTHLY_CACHE")
MONTHLY_FMT=$(printf '$%.0f' "$MONTHLY_COST")

# Effort level (only present when the model supports it)
EFFORT=$(echo "$input" | jq -r '.effort.level // empty')
MODEL_SEG="${BOLD}${CLAUDE}${MODEL}${RESET}"
# Effort color: Claude color at low/medium, shifting toward red as effort rises
case "$EFFORT" in
  high)  EFFORT_COLOR='\033[38;5;203m' ;;
  xhigh) EFFORT_COLOR='\033[38;5;196m' ;;
  max)   EFFORT_COLOR='\033[1;38;5;160m' ;;
  *)     EFFORT_COLOR="$CLAUDE" ;;
esac
[ -n "$EFFORT" ] && MODEL_SEG="${MODEL_SEG} ${EFFORT_COLOR}${EFFORT}${RESET}"

# Subscription usage windows (only present for Pro/Max after first API response)
# Time left until a window resets, from a Unix epoch (e.g. 3h12m, 5d2h, 14m)
fmt_remaining() {
  local left=$(($1 - $(date +%s)))
  [ "$left" -lt 0 ] && left=0
  if [ "$left" -ge 86400 ]; then printf '%dd%dh' $((left / 86400)) $((left % 86400 / 3600))
  elif [ "$left" -ge 3600 ]; then printf '%dh%02dm' $((left / 3600)) $((left % 3600 / 60))
  else printf '%dm' $((left / 60)); fi
}
fmt_limit() {
  local used=$1 resets=$2
  [ -z "$used" ] && return
  used=${used%.*}
  local color="$GREEN"
  [ "$used" -ge 90 ] && color="$RED" || { [ "$used" -ge 70 ] && color="$YELLOW"; }
  printf "%b%s%%%b" "$color" "$used" "$RESET"
  [ -n "$resets" ] && printf " %b↻ %s%b" "$GRAY" "$(fmt_remaining "${resets%.*}")" "$RESET"
}
FIVE=$(fmt_limit "$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')" "$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')")
WEEK=$(fmt_limit "$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')" "$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')")
LIMITS=""
[ -n "$FIVE" ] && LIMITS="$FIVE"
[ -n "$WEEK" ] && LIMITS="${LIMITS:+$LIMITS  }$WEEK"

SEP="  ${GRAY}│${RESET}  "
OUT="${MODEL_SEG}${SEP}${BAR} ${SOFT}${PCT}%${RESET}"
[ -n "$LIMITS" ] && OUT="${OUT}${SEP}${LIMITS}"
OUT="${OUT}${SEP}${YELLOW}${COST_FMT}${RESET} ${GRAY}· ${MONTHLY_FMT}/mo${RESET}${SEP}${GRAY}${DUR}${RESET}"
echo -e "$OUT"
