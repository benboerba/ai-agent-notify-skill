#!/usr/bin/env bash
set -u

CONFIG_FILE="${AI_AGENT_NOTIFY_CONFIG:-$HOME/.config/ai-agent-notify/config.env}"
STATE_DIR="${AI_AGENT_NOTIFY_STATE_DIR:-$HOME/.local/state/ai-agent-notify}"
LOG_FILE="$STATE_DIR/notify.log"
DRY_RUN=0

for ARG in "$@"; do
  [[ "$ARG" == "--dry-run" ]] && DRY_RUN=1
done

if [[ -f "$CONFIG_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$CONFIG_FILE"
fi

MODE="${NOTIFY_MODE:-}"
if [[ "$MODE" != "bark" && "$MODE" != "wechat" && "$MODE" != "both" ]]; then
  exit 2
fi

event_name() {
  local arg
  for arg in "$@"; do
    case "$arg" in
      turn-ended|task-complete|manual-test|test|test-run|--dry-run|"") ;;
      \{*)
        python3 -c '
import json, sys
try:
    data=json.loads(sys.argv[1])
except Exception:
    raise SystemExit
for key in ("thread_name","session_name","conversation_name","title","name"):
    value=data.get(key)
    if isinstance(value,str) and value.strip():
        print(value.strip()[:100]); break
' "$arg" 2>/dev/null && return 0
        ;;
      *) printf '%s\n' "$arg"; return 0 ;;
    esac
  done
}

NAME="$(event_name "$@")"
NAME="${NAME:-当前 AI Agent 任务}"
TITLE="${NOTIFY_TITLE:-AI Agent 已完成：${NAME}}"
BODY="${NOTIFY_BODY:-任务「${NAME}」已经结束，可以回来查看结果了。}"
WECHAT_MESSAGE="✅ ${TITLE}

${BODY}"

if [[ "$DRY_RUN" -eq 1 ]]; then
  printf '{"ok":true,"dryRun":true,"mode":"%s"}\n' "$MODE"
  exit 0
fi

mkdir -p "$STATE_DIR"
BARK_STATUS="skipped"
WECHAT_STATUS="skipped"
FAILED=0

if [[ "$MODE" == "bark" || "$MODE" == "both" ]]; then
  if [[ -z "${BARK_ENDPOINT:-}" ]]; then
    BARK_STATUS="missing-config"
    FAILED=1
  elif curl -fsS --max-time 12 -G "$BARK_ENDPOINT" \
    --data-urlencode "title=$TITLE" \
    --data-urlencode "body=$BODY" \
    --data-urlencode "group=${BARK_GROUP:-AI Agent}" \
    --data-urlencode "sound=${BARK_SOUND:-bell}" >/dev/null; then
    BARK_STATUS="sent"
  else
    BARK_STATUS="failed"
    FAILED=1
  fi
fi

if [[ "$MODE" == "wechat" || "$MODE" == "both" ]]; then
  OPENCLAW_BIN="${OPENCLAW_BIN:-$HOME/.openclaw/bin/openclaw}"
  if [[ ! -x "$OPENCLAW_BIN" || -z "${OPENCLAW_WEIXIN_ACCOUNT:-}" || -z "${OPENCLAW_WEIXIN_TARGET:-}" ]]; then
    WECHAT_STATUS="missing-config"
    FAILED=1
  else
    if OUTPUT="$("$OPENCLAW_BIN" message send \
      --channel openclaw-weixin \
      --account "$OPENCLAW_WEIXIN_ACCOUNT" \
      --target "$OPENCLAW_WEIXIN_TARGET" \
      --message "$WECHAT_MESSAGE" \
      --json 2>&1)" && python3 - "$OUTPUT" <<'PY'
import json, sys
data=json.loads(sys.argv[1])
payload=data.get("payload") or {}
outcomes=payload.get("payloadOutcomes") or []
if payload.get("deliveryStatus") != "sent" or not outcomes or any(x.get("status") != "sent" for x in outcomes):
    raise SystemExit(1)
PY
    then
      WECHAT_STATUS="sent"
    else
      WECHAT_STATUS="failed"
      FAILED=1
    fi
  fi
fi

printf '[%s] mode=%s bark=%s wechat=%s event=%s\n' \
  "$(date '+%Y-%m-%d %H:%M:%S')" "$MODE" "$BARK_STATUS" "$WECHAT_STATUS" "$NAME" >>"$LOG_FILE"
printf '{"ok":%s,"mode":"%s","bark":"%s","wechat":"%s"}\n' \
  "$([[ "$FAILED" -eq 0 ]] && printf true || printf false)" "$MODE" "$BARK_STATUS" "$WECHAT_STATUS"
exit "$FAILED"
