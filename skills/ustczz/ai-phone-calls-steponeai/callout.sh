#!/bin/bash
# Stepone AI 外呼脚本
# 用法: ./callout.sh "手机号" "外呼需求内容"

# 检查环境变量
if [ -z "$STEPONEAI_API_KEY" ]; then
    # 尝试从文件读取
    if [ -f ~/.clawd/secrets.json ]; then
        API_KEY=$(grep -o '"steponeai_api_key"[[:space:]]*:[[:space:]]*"[^"]*"' ~/.clawd/secrets.json | sed 's/.*"\([^"]*\)"$/\1/')
        if [ -n "$API_KEY" ]; then
            export STEPONEAI_API_KEY="$API_KEY"
        fi
    fi
    
    if [ -z "$STEPONEAI_API_KEY" ]; then
        echo "错误: 请设置 STEPONEAI_API_KEY 环境变量"
        echo ""
        echo "方法1 - 环境变量:"
        echo '  export STEPONEAI_API_KEY="aicall_xxxxxxxxxxxxx"'
        echo ""
        echo "方法2 - secrets文件:"
        echo '  echo "{ \"steponeai_api_key\": \"aicall_xxx\" }" > ~/.clawd/secrets.json'
        exit 1
    fi
fi

PHONES="$1"
REQUIREMENT="$2"

if [ -z "$PHONES" ] || [ -z "$REQUIREMENT" ]; then
    echo "用法: $0 <手机号> <外呼需求>"
    echo "示例: $0 \"13800138000\" \"通知您明天上午9点开会\""
    exit 1
fi

API_URL="https://open-skill-api.steponeai.com/api/v1/callinfo/initiate_call"

RESPONSE=$(curl -s -X POST "$API_URL" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $STEPONEAI_API_KEY" \
    -d "{
        \"phones\": \"$PHONES\",
        \"user_requirement\": \"$REQUIREMENT\"
    }")

echo "$RESPONSE"

# 提取 call_id 供后续查询使用
CALL_ID=$(echo "$RESPONSE" | grep -o '"call_id":"[^"]*"' | cut -d'"' -f4)
if [ -z "$CALL_ID" ]; then
    CALL_ID=$(echo "$RESPONSE" | grep -o '"call_id": "[^"]*"' | cut -d'"' -f4)
fi

if [ -n "$CALL_ID" ]; then
    echo ""
    echo "=== CALL_ID: $CALL_ID ==="
    echo "使用此ID查询通话记录: ./callinfo.sh $CALL_ID"
fi
