# Slackbot Integration Guide

## Overview
Your URL shortener backend is now ready for Slackbot integration! Here's everything you need to know.

## Bot-Specific Endpoints

### 1. Shorten URL (Bot)
```bash
POST /api/bot/shorten
Headers: 
  X-API-Key: your-api-key
  Content-Type: application/json

Body:
{
  "url": "https://example.com/very-long-url",
  "custom_code": "slack-link" (optional),
  "expires_at": "2024-12-31T23:59:59" (optional)
}

Response:
{
  "id": 1,
  "original_url": "https://example.com/very-long-url",
  "short_code": "abc123",
  "short_url": "https://your-domain.com/abc123",
  "created_at": "2024-09-26T12:00:00",
  "click_count": 0,
  "expires_at": null
}
```

### 2. Get URL Stats (Bot)
```bash
GET /api/bot/stats/abc123
Headers: 
  X-API-Key: your-api-key

Response:
{
  "short_code": "abc123",
  "original_url": "https://example.com/very-long-url",
  "click_count": 42,
  "created_at": "2024-09-26T12:00:00"
}
```

### 3. List Bot URLs
```bash
GET /api/bot/urls
Headers: 
  X-API-Key: your-api-key

Response: [array of URL objects, latest 100]
```

## Environment Variables
Make sure these are set in your production environment:

```bash
API_KEY=your-secure-api-key-here
ENVIRONMENT=production
BASE_URL=https://your-domain.com
DOMAIN=your-domain.com
```

## Slackbot Implementation Tips

### 1. Basic Slash Command Example
```javascript
// /shorten https://example.com/long-url
app.command('/shorten', async ({ command, ack, respond }) => {
  await ack();
  
  const url = command.text.trim();
  if (!url) {
    return await respond("Please provide a URL to shorten: `/shorten https://example.com`");
  }
  
  try {
    const response = await fetch('https://your-domain.com/api/bot/shorten', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': process.env.URL_SHORTENER_API_KEY
      },
      body: JSON.stringify({ url })
    });
    
    const data = await response.json();
    
    await respond({
      text: `Shortened URL: ${data.short_url}`,
      response_type: 'in_channel'
    });
  } catch (error) {
    await respond("Sorry, I couldn't shorten that URL. Please try again.");
  }
});
```

### 2. Stats Command Example
```javascript
// /urlstats abc123
app.command('/urlstats', async ({ command, ack, respond }) => {
  await ack();
  
  const shortCode = command.text.trim();
  if (!shortCode) {
    return await respond("Please provide a short code: `/urlstats abc123`");
  }
  
  try {
    const response = await fetch(`https://your-domain.com/api/bot/stats/${shortCode}`, {
      headers: {
        'X-API-Key': process.env.URL_SHORTENER_API_KEY
      }
    });
    
    const stats = await response.json();
    
    await respond({
      text: `📊 Stats for ${stats.short_code}:\n` +
            `🔗 Original: ${stats.original_url}\n` +
            `👆 Clicks: ${stats.click_count}\n` +
            `📅 Created: ${stats.created_at}`,
      response_type: 'ephemeral'
    });
  } catch (error) {
    await respond("Couldn't find stats for that short code.");
  }
});
```

### 3. Custom Code Example
```javascript
// /shorten https://example.com mycode
app.command('/shorten', async ({ command, ack, respond }) => {
  await ack();
  
  const parts = command.text.trim().split(' ');
  const url = parts[0];
  const customCode = parts[1];
  
  const body = { url };
  if (customCode) {
    body.custom_code = customCode;
  }
  
  // ... rest of implementation
});
```

## Security Notes

1. **API Key**: Store your API key securely in environment variables
2. **Rate Limiting**: The backend has built-in rate limiting (60 requests/minute by default)
3. **Validation**: URLs are validated before shortening
4. **Bot User**: A special "slackbot" user is automatically created to own all bot-generated URLs

## Error Handling

The API returns standard HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid URL, custom code already exists)
- `404`: Not Found (URL doesn't exist)
- `429`: Rate Limited
- `500`: Server Error

## Testing

Test your integration using curl:

```bash
# Shorten a URL
curl -X POST https://your-domain.com/api/bot/shorten \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"url": "https://example.com"}'

# Get stats
curl -H "X-API-Key: your-api-key" \
  https://your-domain.com/api/bot/stats/abc123

# List all bot URLs
curl -H "X-API-Key: your-api-key" \
  https://your-domain.com/api/bot/urls
```

## Next Steps

1. Set up your Slackbot project
2. Install the Slack SDK (`@slack/bolt` for Node.js)
3. Configure your API key
4. Implement the slash commands
5. Deploy and test!

Happy coding! 🚀