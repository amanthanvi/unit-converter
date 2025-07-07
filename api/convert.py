import json
from urllib.parse import parse_qs
from converter import UnitConverter

def handler(request, context):
    """
    Vercel serverless function to convert units.
    """
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    # Handle OPTIONS request for CORS
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # Only allow POST requests
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        # Parse request body
        body = request.body.decode('utf-8') if request.body else ''
        
        # Try to parse as JSON first
        try:
            data = json.loads(body)
            value = float(data.get('value'))
            from_unit = data.get('from_unit')
            to_unit = data.get('to_unit')
        except json.JSONDecodeError:
            # Fall back to form data parsing
            parsed_data = parse_qs(body)
            value = float(parsed_data.get('value', [None])[0])
            from_unit = parsed_data.get('from_unit', [None])[0]
            to_unit = parsed_data.get('to_unit', [None])[0]
        
        if not all([value is not None, from_unit, to_unit]):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Missing required parameters'})
            }
        
        # Initialize converter
        converter = UnitConverter()
        
        # Perform conversion
        result = converter.convert(value, from_unit, to_unit)
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(result)
        }
        
    except ValueError as e:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Conversion failed: ' + str(e)})
        }