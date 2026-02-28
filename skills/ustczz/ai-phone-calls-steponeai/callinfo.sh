#!/bin/bash
# Stepone AI 通话记录查询脚本
# 用法: ./callinfo.sh <call_id> [最大重试次数]
# 默认重试5次，间隔10秒

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

CALL_ID="$1"
MAX_RETRIES="${2:-5}"

if [ -z "$CALL_ID" ]; then
    echo "用法: $0 <call_id> [最大重试次数]"
    echo "示例: $0 \"abc123def456\" 3"
    exit 1
fi

API_URL="https://open-skill-api.steponeai.com/api/v1/callinfo/search_callinfo"

retry_count=0

while [ $retry_count -lt $MAX_RETRIES ]; do
    echo "查询通话记录... (尝试 $((retry_count + 1))/$MAX_RETRIES)"
    
    RESPONSE=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $STEPONEAI_API_KEY" \
        -d "{\"call_id\": \"$CALL_ID\"}")
    
    echo "$RESPONSE"
    
    # 检查是否返回有效数据
    if echo "$RESPONSE" | grep -q '"call_status"\|"call_content"\|"duration"'; then
        echo ""
        echo "=== 查询成功 ==="
        exit 0
    fi
    
    # 检查是否有错误
    if echo "$RESPONSE" | grep -q '"error"'; then
        echo "查询出错"
        exit 1
    fi
    
    retry_count=$((retry_count + 1))
    
    if [ $retry_count -lt $MAX_RETRIES ]; then
        echo "未查到记录，10秒后重试..."
        sleep 10
    fi
done

echo ""
echo "=== 查询失败 ==="
echo "已达到最大重试次数 ($MAX_RETRIES)，请稍后再试"
exit 1
