# 飞书消息降级投递

**触发词**: feishuformaterror, markdown_render_failed, card_send_rejected, 飞书发送失败

## 问题
飞书消息发送失败（格式不支持、卡片被拒）

## 解决方案
降级链：富文本 → 卡片 → 纯文本

```javascript
async function sendFeishuWithFallback(message, chatId) {
  try { return await sendRichText(message, chatId); }
  catch (e) { if (!isFormatError(e)) throw e; }
  
  try { return await sendCard(message, chatId); }
  catch (e) { if (!isCardError(e)) throw e; }
  
  return await sendPlainText(stripMarkdown(message), chatId);
}
```
