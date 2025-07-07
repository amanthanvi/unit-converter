import json
from converter import UnitConverter

def handler(request, context):
    """
    Vercel serverless function to get units for a specific category.
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
        category = request.args.get('category')
        
        if not category:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Category parameter is required'})
            }
        
        # Initialize converter
        converter = UnitConverter()
        
        # Get units
        units = converter.get_units(category)
        
        if not units:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Invalid category'})
            }
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(units)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }