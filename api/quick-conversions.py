import json
from converter import UnitConverter

def handler(request, context):
    """
    Vercel serverless function to get quick conversions for a given value and unit.
    """
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    # Handle OPTIONS request for CORS
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # Only allow GET requests
    if request.method != 'GET':
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        # Parse query parameters
        value = request.args.get('value')
        unit = request.args.get('unit')
        
        if value:
            value = float(value)
        
        if not all([value is not None, unit]):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Missing required parameters'})
            }
        
        # Initialize converter
        converter = UnitConverter()
        
        # Get quick conversions
        conversions = converter.get_quick_conversions(value, unit)
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(conversions)
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
            'body': json.dumps({'error': 'Failed to get quick conversions: ' + str(e)})
        }