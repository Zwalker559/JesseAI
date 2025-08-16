import json
import ai_core

def handler(event, context):
    try:
        body = json.loads(event['body'])
        user_id = body.get('user_id', 'web_user')
        message = body.get('message', '')
        guild_id = 'web_chat'

        ai_core.store_message(guild_id, user_id, user_msg=message)
        reply = ai_core.generate_response(guild_id, user_id, message)
        ai_core.store_message(guild_id, user_id, bot_msg=reply)

        return {
            'statusCode': 200,
            'body': json.dumps({'reply': reply})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
