import json
from converter import UnitConverter

def handler(request, context):
    """Handle GET request for categories"""
    try:
        # Initialize converter
        converter = UnitConverter()
        
        # Get categories
        categories = converter.get_categories()
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(categories)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }